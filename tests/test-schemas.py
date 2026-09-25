#!/usr/bin/env python3
"""Kit JSON files satisfy config/schemas, and the stdlib validator agrees with jsonschema."""
from __future__ import annotations

import copy
import importlib.util
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("apk_validate_schemas", ROOT / "scripts" / "validate_schemas.py")
assert spec and spec.loader
schemas = importlib.util.module_from_spec(spec)
spec.loader.exec_module(schemas)

try:
    import jsonschema  # optional reference implementation
except ImportError:
    jsonschema = None

REPLACEMENTS = (None, True, 0, 1, -1, "", " x", "bad id", "a" * 64, [], [""], ["x", "x"], {}, {"x": 1})


def paths(value, prefix=()):
    yield prefix
    if isinstance(value, dict):
        for key, child in value.items():
            yield from paths(child, prefix + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from paths(child, prefix + (index,))


def mutated(data, path, replacement):
    clone = copy.deepcopy(data)
    if not path:
        return replacement
    node = clone
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = replacement
    return clone


def removed(data, path):
    clone = copy.deepcopy(data)
    node = clone
    for part in path[:-1]:
        node = node[part]
    del node[path[-1]]
    return clone


def main() -> None:
    for name, schema_name in schemas.KIT_FILES:
        errors = schemas.validate_file(ROOT / name, schema_name)
        assert errors == [], (name, errors)
    for name, schema_name in schemas.PROJECT_FILES:
        template = ROOT / "templates" / Path(name).name
        assert schemas.validate_file(template, schema_name) == []

    # Designed failures the schemas must reject.
    registry = json.loads((ROOT / "config/workflow-registry.json").read_text(encoding="utf-8"))
    binding = json.loads((ROOT / "templates/apk.json").read_text(encoding="utf-8"))
    project = json.loads((ROOT / "templates/project.json").read_text(encoding="utf-8"))
    rejects = [
        ("workflow-registry", mutated(registry, ("schema_version",), True)),
        ("workflow-registry", mutated(registry, ("composition", "method_max"), 0)),
        ("workflow-registry", mutated(registry, ("primary_pipelines", "general", "selectors", "domains"), ["Bad Id"])),
        ("workflow-registry", mutated(registry, ("modules", "stages", "implementation", "prompt"), "notes/x.md")),
        ("workflow-registry", {**registry, "unexpected": 1}),
        ("apk-binding", mutated(binding, ("content_sha256",), "abc")),
        ("apk-binding", mutated(binding, ("version",), "../escape")),
        ("apk-binding", mutated(binding, ("package",), "other-kit")),
        ("apk-binding", removed(binding, ("version",))),
        ("project", mutated(project, ("domain",), "software")),
        ("project", removed(project, ("status",))),
    ]
    for schema_name, data in rejects:
        assert schemas.validate(data, schema_name), (schema_name, "should be rejected")
    # Projects own project.json: extra keys are allowed there.
    assert schemas.validate({**project, "team": "local"}, "project") == []

    try:
        schemas.Validator({"type": "string", "format": "email"}).errors("x", {"type": "string", "format": "email"})
    except ValueError as error:
        assert "unsupported schema keyword" in str(error)
    else:
        raise AssertionError("unsupported keyword was not rejected")

    if jsonschema is None:
        print("schema tests: PASS (jsonschema not installed; agreement check skipped)")
        return
    rng = random.Random(20260925)
    checked = 0
    for name, schema_name in schemas.KIT_FILES:
        data = json.loads((ROOT / name).read_text(encoding="utf-8"))
        schema = schemas.load_schema(schema_name)
        jsonschema.Draft202012Validator.check_schema(schema)
        reference = jsonschema.Draft202012Validator(schema)
        all_paths = [p for p in paths(data) if p]
        cases = [removed(data, p) for p in rng.sample(all_paths, min(60, len(all_paths)))]
        cases += [mutated(data, p, rng.choice(REPLACEMENTS)) for p in rng.choices(all_paths, k=240)]
        for case in cases:
            ours = not schemas.validate(case, schema_name)
            theirs = reference.is_valid(case)
            assert ours == theirs, (schema_name, ours, theirs)
            checked += 1
    print(f"schema tests: PASS ({checked} mutations agree with jsonschema)")


if __name__ == "__main__":
    main()
