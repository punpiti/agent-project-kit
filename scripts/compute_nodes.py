#!/usr/bin/env python3
"""Show which compute nodes are up, how loaded they are, and pick one for a job.

The node inventory is a machine-local JSON file (see
templates/compute-nodes.example.json), never part of the package: it names
machines and SSH aliases. Lookup order: --inventory, $APK_COMPUTE_NODES,
~/.config/agent-project-kit/compute-nodes.json.

A node is probed locally when its `hostnames` match this machine, otherwise
over `ssh <alias>` (BatchMode, short timeout). A node with `via` is reached
from the node named there, which holds the SSH key: `ssh <via> ssh <alias>`.
Nodes listed in its `direct_from` have their own key and connect directly.
Probes only read /proc, nproc, df, nvidia-smi, and `rclone listremotes`.

Besides SSD/HDD (`storage`, tiers hot/cold), each node declares how it reaches
the two sources of truth in DATA_FLOW_POLICY.md: `git` (GitHub access) and
`cloud_drives` (tier `durable`: a synced folder path or an rclone remote). The
probe turns these into channels: installed tools (git, rsync, rclone, gh),
`github` (declared; verified with --check-github), and one slug per cloud drive
whose path or remote is present (e.g. `onedrive`, `googledrive`). `--needs`
filters on them, so a job that reads OneDrive never lands on a node without it.

`network.metered` is false, true, or "sometimes". Unless it is false, a
Windows/WSL2 node reports its live connection cost (`Unrestricted` means
unmetered). Unmetered nodes get the `unmetered` channel. `egress` returns the
first node in the inventory's `egress` list that is up, unmetered, and has
`github`: use it for pushes, clones, and large downloads.

Free capacity is `threads - load1`, scaled by the node's optional
`thread_weight`. `pick` returns the reachable node with the most free capacity
that meets --min-threads/--min-mem-gb/--gpu, so a big node half loaded still
beats a small idle one. Nothing is dispatched except by `run`.

  python3 scripts/compute_nodes.py status
  python3 scripts/compute_nodes.py status --watch 30
  python3 scripts/compute_nodes.py pick --min-threads 8 --json
  python3 scripts/compute_nodes.py pick --needs git,github --check-github
  python3 scripts/compute_nodes.py egress
  python3 scripts/compute_nodes.py run --min-threads 8 --cwd /data/job -- python3 train.py
"""
from __future__ import annotations
import argparse, json, os, shlex, socket, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DEFAULT_INVENTORY = Path.home() / ".config" / "agent-project-kit" / "compute-nodes.json"
CONNECT_TIMEOUT = 8
PROBE_TIMEOUT = 30
SSH_OPTS = ("-o", "BatchMode=yes", "-o", f"ConnectTimeout={CONNECT_TIMEOUT}")

# Prints key=value lines; every command is optional on the target.
PROBE_SCRIPT = r"""
echo "hostname=$(hostname)"
echo "threads=$(nproc 2>/dev/null || getconf _NPROCESSORS_ONLN)"
read l1 l5 l15 _ < /proc/loadavg; echo "load1=$l1"; echo "load5=$l5"
awk '/^MemTotal:/{print "mem_total_kb="$2} /^MemAvailable:/{print "mem_avail_kb="$2}' /proc/meminfo
for m in __MOUNTS__; do
  [ -d "$m" ] && df -Pk "$m" 2>/dev/null | awk -v m="$m" 'NR==2{print "disk_free_kb:"m"="$4}'
done
for c in git rsync rclone gh; do command -v "$c" >/dev/null 2>&1 && echo "has=$c"; done
for p in __CLOUD_PATHS__; do [ -d "$p" ] && echo "path_ok=$p"; done
command -v rclone >/dev/null 2>&1 && rclone listremotes 2>/dev/null | sed 's/^/rclone_remote=/'
__GITHUB_CHECK__
__METERED_CHECK__
PATH="$PATH:/usr/lib/wsl/lib"
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null \
    | head -1 | awk -F', *' '{print "gpu_util="$1; print "gpu_mem_used_mb="$2; print "gpu_mem_total_mb="$3}'
fi
"""
GITHUB_CHECK = ('ssh -n -o BatchMode=yes -o ConnectTimeout=6 -T git@github.com 2>&1 '
                '| grep -q "successfully authenticated" && echo "github_ok=1"')
METERED_CHECK = r"""PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
[ -x "$PS" ] && echo "net_cost=$(timeout 20 "$PS" -NoProfile -Command '[void][Windows.Networking.Connectivity.NetworkInformation,Windows.Networking.Connectivity,ContentType=WindowsRuntime]; $p=[Windows.Networking.Connectivity.NetworkInformation]::GetInternetConnectionProfile(); if ($p) { $p.GetConnectionCost().NetworkCostType } else { "None" }' 2>/dev/null | tr -d '\r')"
"""
LIST_KEYS = ("has", "path_ok", "rclone_remote")
TEXT_KEYS = ("hostname", "net_cost")


def load_inventory(path: str | None) -> tuple[dict, Path]:
    candidates = [path, os.environ.get("APK_COMPUTE_NODES"), str(DEFAULT_INVENTORY)]
    for c in candidates:
        if c and Path(c).expanduser().is_file():
            p = Path(c).expanduser()
            data = json.loads(p.read_text(encoding="utf-8"))
            validate_inventory(data)
            return data, p
    sys.exit("compute_nodes: no inventory found. Copy templates/compute-nodes.example.json to "
             f"{DEFAULT_INVENTORY} or set APK_COMPUTE_NODES.")


def validate_inventory(data: dict) -> None:
    nodes = data.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("inventory needs a non-empty 'nodes' list")
    names = [n.get("name") for n in nodes]
    if len(set(names)) != len(names) or not all(names):
        raise ValueError("every node needs a unique 'name'")
    for n in nodes:
        via = n.get("via")
        if via and via not in names:
            raise ValueError(f"node {n['name']}: via {via!r} is not a node")
        if via == n["name"]:
            raise ValueError(f"node {n['name']}: via points to itself")
    for key in ("hubs", "egress"):
        unknown = [x for x in data.get(key, []) if x not in names]
        if unknown:
            raise ValueError(f"{key} names unknown nodes: {unknown}")


def short(host: str) -> str:
    return host.split(".")[0].lower()


def self_node(nodes: list[dict], hostname: str | None = None) -> str | None:
    me = short(hostname or socket.gethostname())
    for n in nodes:
        if me in {short(h) for h in n.get("hostnames", [n["name"]])}:
            return n["name"]
    return None


def route(nodes: list[dict], name: str, here: str | None, seen: tuple = ()) -> list[str] | None:
    """SSH hops from `here` to node `name`; [] means local, None means no path."""
    if name == here:
        return []
    if name in seen:
        return None
    node = next(n for n in nodes if n["name"] == name)
    via = node.get("via")
    if via:
        if via == here or here in node.get("direct_from", []):
            return [node["ssh"]] if node.get("ssh") else None
        prefix = route(nodes, via, here, seen + (name,))
        if prefix is None or not node.get("ssh"):
            return None
        return prefix + [node["ssh"]]
    return [node["ssh"]] if node.get("ssh") else None


def wrap(hops: list[str], remote: str) -> list[str]:
    """Build argv that runs `remote` (a shell string) after the given hops."""
    if not hops:
        return ["bash", "-c", remote]
    cmd = remote
    for alias in reversed(hops[1:]):
        cmd = shlex.join(["ssh", *SSH_OPTS, alias, cmd])
    return ["ssh", *SSH_OPTS, hops[0], cmd]


def parse_probe(text: str) -> dict:
    out: dict = {"disk_free_gb": {}, **{k: [] for k in LIST_KEYS}}
    for line in text.splitlines():
        key, sep, val = line.partition("=")
        if not sep:
            continue
        if key in LIST_KEYS:
            out[key].append(val.strip())
        elif key == "github_ok":
            out[key] = True
        elif key.startswith("disk_free_kb:"):
            out["disk_free_gb"][key.split(":", 1)[1]] = round(int(val) / 1048576, 1)
        elif key in TEXT_KEYS:
            out[key] = val.strip()
        else:
            try:
                out[key] = float(val)
            except ValueError:
                pass
    if "mem_avail_kb" in out:
        out["mem_avail_gb"] = round(out.pop("mem_avail_kb") / 1048576, 1)
    if "mem_total_kb" in out:
        out["mem_total_gb"] = round(out.pop("mem_total_kb") / 1048576, 1)
    return out


def slug(provider: str) -> str:
    return "".join(ch for ch in provider.lower() if ch.isalnum())


def channels(node: dict, data: dict, github_checked: bool = False) -> list[str]:
    """Tools present, GitHub access, and cloud drives reachable on this node."""
    caps = set(data.get("has", []))
    if (node.get("git") or {}).get("github") and (data.get("github_ok") or not github_checked):
        caps.add("github")
    for drive in node.get("cloud_drives", []):
        path, remote = drive.get("path"), drive.get("rclone_remote")
        if (path and path in data.get("path_ok", [])) or (remote and remote in data.get("rclone_remote", [])):
            caps.add(slug(drive["provider"]))
    if not metered(node, data):
        caps.add("unmetered")
    return sorted(caps)


def metered(node: dict, data: dict) -> bool:
    """Declared false stays unmetered; otherwise trust the live cost, else assume metered."""
    declared = (node.get("network") or {}).get("metered", "sometimes")
    if declared is False:
        return False
    cost = data.get("net_cost")
    if cost:
        return cost != "Unrestricted"
    return True


def probe(nodes: list[dict], node: dict, here: str | None, check_github: bool = False) -> dict:
    result = {"name": node["name"], "role": node.get("role", "compute")}
    hops = route(nodes, node["name"], here)
    if hops is None:
        return {**result, "up": False, "error": "no SSH path from this machine"}
    mounts = " ".join(shlex.quote(s["mount"]) for s in node.get("storage", []) if s.get("mount"))
    clouds = " ".join(shlex.quote(d["path"]) for d in node.get("cloud_drives", []) if d.get("path"))
    script = (PROBE_SCRIPT.replace("__MOUNTS__", mounts or "/").replace("__CLOUD_PATHS__", clouds)
              .replace("__GITHUB_CHECK__", GITHUB_CHECK if check_github else "")
              .replace("__METERED_CHECK__", "" if (node.get("network") or {}).get("metered") is False
                       else METERED_CHECK))
    result["route"] = hops
    try:
        proc = subprocess.run(wrap(hops, "bash -s"), input=script, capture_output=True,
                              text=True, timeout=PROBE_TIMEOUT)
    except subprocess.TimeoutExpired:
        return {**result, "up": False, "error": "probe timed out"}
    if proc.returncode != 0 or "threads=" not in proc.stdout:
        err = (proc.stderr.strip().splitlines() or ["probe failed"])[-1]
        return {**result, "up": False, "error": err}
    data = parse_probe(proc.stdout)
    threads = data.get("threads", 0)
    free = max(0.0, threads - data.get("load1", threads))
    data["free_threads"] = round(free, 1)
    data["score"] = round(free * float(node.get("thread_weight", 1.0)), 1)
    data["channels"] = channels(node, data, check_github)
    return {**result, "up": True, **data}


def probe_all(inv: dict, here: str | None, check_github: bool = False) -> list[dict]:
    nodes = inv["nodes"]
    with ThreadPoolExecutor(max_workers=len(nodes)) as pool:
        return list(pool.map(lambda n: probe(nodes, n, here, check_github), nodes))


def eligible(inv: dict, status: dict, min_threads: float, min_mem_gb: float, gpu: bool,
             needs: tuple = ()) -> bool:
    node = next(n for n in inv["nodes"] if n["name"] == status["name"])
    if not status.get("up") or node.get("dispatch", True) is False:
        return False
    if status.get("free_threads", 0) < min_threads or status.get("mem_avail_gb", 0) < min_mem_gb:
        return False
    if not set(needs) <= set(status.get("channels", [])):
        return False
    return not gpu or "gpu_mem_total_mb" in status


def rank(inv: dict, statuses: list[dict], min_threads: float = 1, min_mem_gb: float = 0,
         gpu: bool = False, needs: tuple = ()) -> list[dict]:
    prio = {n["name"]: n.get("priority", 0) for n in inv["nodes"]}
    ok = [s for s in statuses if eligible(inv, s, min_threads, min_mem_gb, gpu, needs)]
    return sorted(ok, key=lambda s: (-s["score"], -prio[s["name"]], s["name"]))


def egress_node(order: list[str], statuses: dict) -> str | None:
    for name in order:
        s = statuses.get(name, {})
        if s.get("up") and {"github", "unmetered"} <= set(s.get("channels", [])):
            return name
    return None


def print_table(statuses: list[dict], here: str | None) -> None:
    print(f"{'node':<12} {'role':<8} {'state':<6} {'threads':>7} {'load1':>6} {'free':>5} "
          f"{'mem free':>9} {'gpu':>5}  {'channels':<58} disks free")
    for s in statuses:
        mark = "*" if s["name"] == here else " "
        if not s["up"]:
            print(f"{s['name'] + mark:<12} {s['role']:<8} {'down':<6} {s['error']}")
            continue
        gpu = f"{s['gpu_util']:.0f}%" if "gpu_util" in s else "-"
        chans = ",".join(s.get("channels", [])) or "-"
        disks = ", ".join(f"{m} {gb:g}G" for m, gb in s["disk_free_gb"].items())
        print(f"{s['name'] + mark:<12} {s['role']:<8} {'up':<6} {s['threads']:>7.0f} {s['load1']:>6.1f} "
              f"{s['free_threads']:>5.1f} {s.get('mem_avail_gb', 0):>7.1f}G {gpu:>5}  {chans:<58} {disks}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--inventory")
    sub = ap.add_subparsers(dest="cmd", required=True)
    st = sub.add_parser("status", help="probe every node")
    st.add_argument("--json", action="store_true")
    st.add_argument("--watch", type=int, metavar="SECONDS")
    st.add_argument("--check-github", action="store_true", help="verify GitHub SSH auth on each node")
    eg = sub.add_parser("egress", help="node for GitHub and large downloads")
    eg.add_argument("--check-github", action="store_true", help="verify GitHub SSH auth on each node")
    eg.add_argument("--json", action="store_true")
    for name in ("pick", "run"):
        p = sub.add_parser(name, help="choose the best node" if name == "pick" else "run a command there")
        p.add_argument("--min-threads", type=float, default=1)
        p.add_argument("--min-mem-gb", type=float, default=0)
        p.add_argument("--gpu", action="store_true", help="require an NVIDIA GPU")
        p.add_argument("--needs", default="", help="comma list of channels, e.g. git,github,onedrive")
        p.add_argument("--check-github", action="store_true", help="verify GitHub SSH auth on each node")
        if name == "pick":
            p.add_argument("--json", action="store_true")
        else:
            p.add_argument("--node", help="skip the choice and use this node")
            p.add_argument("--cwd", help="directory on the target node")
            p.add_argument("command", nargs=argparse.REMAINDER)
    args = ap.parse_args(argv)

    inv, inv_path = load_inventory(args.inventory)
    here = self_node(inv["nodes"])

    if args.cmd == "status":
        while True:
            statuses = probe_all(inv, here, args.check_github)
            if args.json:
                print(json.dumps({"here": here, "inventory": str(inv_path), "nodes": statuses},
                                 ensure_ascii=False, indent=2))
            else:
                if args.watch:
                    print("\033[2J\033[H" + time.strftime("%Y-%m-%d %H:%M:%S"), f"(here: {here or 'unknown'})")
                print_table(statuses, here)
            if not args.watch:
                return 0
            time.sleep(args.watch)

    if args.cmd == "egress":
        statuses = {s["name"]: s for s in probe_all(inv, here, args.check_github)}
        order = inv.get("egress") or [n["name"] for n in sorted(inv["nodes"], key=lambda n: -n.get("priority", 0))]
        best = egress_node(order, statuses)
        if args.json:
            print(json.dumps({"here": here, "egress": best, "order": order,
                              "nodes": list(statuses.values())}, ensure_ascii=False, indent=2))
        elif best:
            print(best)
        if not best:
            print("compute_nodes: no node is up, unmetered, and on GitHub; wait or ask before a "
                  "metered download", file=sys.stderr)
            return 3
        return 0

    if args.cmd == "run" and args.node:
        if args.node not in {n["name"] for n in inv["nodes"]}:
            sys.exit(f"compute_nodes: unknown node {args.node!r}")
        best = {"name": args.node}
    else:
        needs = tuple(n.strip().lower() for n in args.needs.split(",") if n.strip())
        ranked = rank(inv, probe_all(inv, here, args.check_github), args.min_threads, args.min_mem_gb,
                      args.gpu, needs)
        if not ranked:
            print("compute_nodes: no reachable node meets the request", file=sys.stderr)
            return 3
        best = ranked[0]
        if args.cmd == "pick":
            if args.json:
                print(json.dumps({"here": here, "best": best, "ranked": ranked}, ensure_ascii=False, indent=2))
            else:
                print(best["name"])
            return 0

    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        sys.exit("compute_nodes: run needs a command after --")
    hops = route(inv["nodes"], best["name"], here)
    if hops is None:
        sys.exit(f"compute_nodes: no SSH path to {best['name']}")
    remote = shlex.join(command)
    if args.cwd:
        remote = f"cd {shlex.quote(args.cwd)} && {remote}"
    print(f"compute_nodes: running on {best['name']} via {' -> '.join(hops) or 'local'}", file=sys.stderr)
    return subprocess.call(wrap(hops, f"bash -lc {shlex.quote(remote)}"))


if __name__ == "__main__":
    sys.exit(main())
