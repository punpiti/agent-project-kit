#!/usr/bin/env python3
"""compute_nodes.py: inventory validation, SSH routing, probe parsing, ranking."""
import json, socket, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import compute_nodes as cn  # noqa: E402

NODES = [
    {"name": "hub", "hostnames": ["hub-host.example"], "ssh": "hub-wsl", "role": "hub", "priority": 1},
    {"name": "big", "hostnames": ["big"], "ssh": "big", "via": "hub", "direct_from": ["lap"], "priority": 3},
    {"name": "desk", "hostnames": ["desk"], "ssh": "desk-wsl"},
    {"name": "lap", "hostnames": ["lap"], "ssh": "lap-wsl", "dispatch": False},
]
INV = {"nodes": NODES}


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def test_validate():
    cn.validate_inventory(INV)
    for bad in ({"nodes": []}, {"nodes": [{"name": "a"}, {"name": "a"}]},
                {"nodes": [{"name": "a", "via": "missing"}]}, {"nodes": [{"name": "a", "via": "a"}]},
                {"nodes": [{"name": "a"}], "egress": ["b"]}):
        try:
            cn.validate_inventory(bad)
        except ValueError:
            continue
        raise AssertionError(f"accepted bad inventory {bad}")


def test_self_and_route():
    check(cn.self_node(NODES, "HUB-HOST") == "hub", "short, case-insensitive hostname match")
    check(cn.self_node(NODES, "nobody") is None, "unknown host")
    check(cn.route(NODES, "hub", "hub") == [], "self is local")
    check(cn.route(NODES, "big", "hub") == ["big"], "direct from the via node")
    check(cn.route(NODES, "big", "lap") == ["big"], "direct_from has its own key")
    check(cn.route(NODES, "big", "desk") == ["hub-wsl", "big"], "through the via node elsewhere")
    check(cn.route(NODES, "big", None) == ["hub-wsl", "big"], "unknown origin goes through via")
    loop = [{"name": "a", "ssh": "a", "via": "b"}, {"name": "b", "ssh": "b", "via": "a"}]
    check(cn.route(loop, "a", None) is None, "via cycle has no route")


def test_wrap_quotes_each_hop():
    check(cn.wrap([], "echo hi") == ["bash", "-c", "echo hi"], "local wrap")
    argv = cn.wrap(["hub-wsl", "big"], "echo 'a b'")
    check(argv[0] == "ssh" and argv[-2] == "hub-wsl", argv)
    check(argv[-1].startswith("ssh ") and "big" in argv[-1] and "'\"'\"'" in argv[-1], argv[-1])


def test_parse_and_rank():
    text = ("hostname=big\nthreads=32\nload1=16.0\nload5=15\nmem_total_kb=134217728\n"
            "mem_avail_kb=104857600\ndisk_free_kb:/data=1048576\ngpu_util=3\ngpu_mem_total_mb=4094\n")
    big = cn.parse_probe(text)
    check(big["threads"] == 32 and big["mem_avail_gb"] == 100.0, big)
    check(big["disk_free_gb"] == {"/data": 1.0}, big["disk_free_gb"])
    statuses = [
        {"name": "hub", "up": True, "free_threads": 8, "score": 8, "mem_avail_gb": 16},
        {"name": "big", "up": True, "free_threads": 16, "score": 16, "mem_avail_gb": 100, "gpu_mem_total_mb": 4094},
        {"name": "lap", "up": True, "free_threads": 20, "score": 20, "mem_avail_gb": 50},
    ]
    check([s["name"] for s in cn.rank(INV, statuses)] == ["big", "hub"], "half-loaded big node wins; lap never dispatched")
    check([s["name"] for s in cn.rank(INV, statuses, min_threads=10)] == ["big"], "min threads")
    check([s["name"] for s in cn.rank(INV, statuses, min_mem_gb=200)] == [], "min mem")
    statuses[1]["up"] = False
    check([s["name"] for s in cn.rank(INV, statuses, gpu=True)] == [], "down node and gpu filter")


def test_channels_and_needs():
    node = {"name": "n", "git": {"github": "ssh"},
            "cloud_drives": [{"provider": "OneDrive", "path": "/od"},
                             {"provider": "Google Drive", "rclone_remote": "gdrive:"},
                             {"provider": "Dropbox", "path": "/missing"}]}
    data = cn.parse_probe("threads=4\nhas=git\nhas=rsync\npath_ok=/od\nrclone_remote=gdrive:\n")
    check(cn.channels(node, data) == ["git", "github", "googledrive", "onedrive", "rsync"], cn.channels(node, data))
    check("github" not in cn.channels(node, data, github_checked=True), "unverified github dropped when checked")
    data["github_ok"] = True
    check("github" in cn.channels(node, data, github_checked=True), "verified github kept")
    check(cn.channels({"name": "bare"}, data) == ["git", "rsync"], "nothing declared, tools only")
    statuses = [
        {"name": "hub", "up": True, "free_threads": 4, "score": 4, "mem_avail_gb": 16, "channels": ["git", "onedrive"]},
        {"name": "big", "up": True, "free_threads": 16, "score": 16, "mem_avail_gb": 100, "channels": ["rsync"]},
    ]
    check([s["name"] for s in cn.rank(INV, statuses, needs=("onedrive",))] == ["hub"], "needs filters")
    check([s["name"] for s in cn.rank(INV, statuses)] == ["big", "hub"], "no needs, capacity wins")


def test_metered_and_egress():
    data = cn.parse_probe("threads=4\nnet_cost=Unrestricted\n")
    check(not cn.metered({"network": {"metered": "sometimes"}}, data), "live Unrestricted is unmetered")
    check(cn.metered({"network": {"metered": "sometimes"}}, {"net_cost": "Fixed"}), "Fixed is metered")
    check(cn.metered({}, {}), "unknown cost is treated as metered")
    check(not cn.metered({"network": {"metered": False}}, {}), "declared unmetered")
    statuses = {
        "hub": {"up": True, "channels": ["github", "unmetered"]},
        "home": {"up": True, "channels": ["github"]},
        "spare": {"up": True, "channels": ["github", "unmetered"]},
    }
    check(cn.egress_node(["hub", "home"], statuses) == "hub", "first in order")
    statuses["hub"]["up"] = False
    check(cn.egress_node(["hub", "home"], statuses) is None, "metered node skipped")
    check(cn.egress_node(["hub", "home", "spare"], statuses) == "spare", "falls through the list")


def test_cli_probes_this_machine():
    me = socket.gethostname()
    inv = {"nodes": [{"name": "here", "hostnames": [me], "storage": [{"mount": "/"}]},
                     {"name": "nowhere", "hostnames": ["nowhere"]}]}
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "nodes.json"
        path.write_text(json.dumps(inv))
        out = subprocess.run([sys.executable, str(ROOT / "scripts" / "compute_nodes.py"),
                              "--inventory", str(path), "status", "--json"],
                             capture_output=True, text=True, timeout=60, check=True).stdout
        data = json.loads(out)
        here, nowhere = data["nodes"]
        check(data["here"] == "here" and here["up"] and here["threads"] >= 1, here)
        check("/" in here["disk_free_gb"], here)
        check(not nowhere["up"] and "no SSH path" in nowhere["error"], nowhere)
        run = subprocess.run([sys.executable, str(ROOT / "scripts" / "compute_nodes.py"),
                              "--inventory", str(path), "run", "--node", "here", "--cwd", tmp,
                              "--", "pwd"], capture_output=True, text=True, timeout=60)
        check(run.returncode == 0 and Path(run.stdout.strip()).resolve() == Path(tmp).resolve(), run)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
    print("compute-nodes tests passed")
