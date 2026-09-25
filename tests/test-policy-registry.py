#!/usr/bin/env python3
"""The registry is the single source for always-on policy text in STARTUP.md."""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("apk_sync_registry", ROOT / "scripts" / "sync_workflow_registry.py")
assert spec and spec.loader
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


def main() -> None:
    registry = json.loads((ROOT / "config" / "workflow-registry.json").read_text(encoding="utf-8"))
    assert sync.policy_errors(registry) == [], sync.policy_errors(registry)

    startup = (ROOT / "STARTUP.md").read_text(encoding="utf-8")
    block = sync.startup_policy_block(registry)
    assert block in startup, "STARTUP.md policy block is stale; run sync_workflow_registry.py --write"
    for key in registry["always_policies"]:
        assert f"- `{key}`: {registry['policies'][key]}" in block, key
    for key in set(registry["policies"]) - set(registry["always_policies"]):
        assert f"`{key}`" not in block, f"non-always policy {key} leaked into STARTUP"

    # Editing policy text in the registry makes the generated block stale.
    edited = copy.deepcopy(registry)
    edited["policies"]["loop-boundary"] += " Extra."
    assert sync.with_startup_block(startup, sync.startup_policy_block(edited)) != startup

    def errors_after(mutate) -> list[str]:
        clone = copy.deepcopy(registry)
        mutate(clone)
        return sync.policy_errors(clone)

    assert any("no policy_sources" in e for e in errors_after(lambda r: r["policy_sources"].pop("loop-boundary")))
    assert any("unknown policy" in e for e in errors_after(lambda r: r["policy_sources"].update(ghost=["AGENTS.md#Core Loop Model"])))
    assert any("source not found" in e for e in errors_after(lambda r: r["policy_sources"].update({"loop-boundary": ["AGENTS.md#No Such Heading"]})))
    assert any("source not found" in e for e in errors_after(lambda r: r["policy_sources"].update({"loop-boundary": ["MISSING.md#Core Loop Model"]})))
    assert any("always_policies names unknown" in e for e in errors_after(lambda r: r["always_policies"].append("ghost")))

    try:
        sync.with_startup_block(startup.replace(sync.POLICY_END, ""), block)
    except SystemExit as error:
        assert "exactly one" in str(error)
    else:
        raise AssertionError("missing end marker was not rejected")

    print("policy registry tests: PASS")


if __name__ == "__main__":
    main()
