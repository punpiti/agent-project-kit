#!/usr/bin/env python3
"""Validate Agent Project Kit JSON files against config/schemas without dependencies.

The schemas are standard JSON Schema (draft 2020-12), so any conforming tool can
use them. This validator implements only the keywords those schemas use and
fails closed on any other keyword, so a schema edit cannot be silently ignored.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "config" / "schemas"

# Canonical kit files and the schema each must satisfy.
KIT_FILES = (
    ("config/workflow-registry.json", "workflow-registry"),
    ("config/routing-rules.json", "routing-rules"),
    ("templates/apk.json", "apk-binding"),
    ("templates/project.json", "project"),
    ("templates/state.json", "legacy-state"),
)
# Project-local files checked with --project, when present.
PROJECT_FILES = ((".ai/apk.json", "apk-binding"), (".ai/project.json", "project"),
                 (".ai/state.json", "legacy-state"))

ANNOTATIONS = {"$schema", "$id", "$defs", "title", "description"}
TYPES = {
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
}


def _same(a: object, b: object) -> bool:
    # JSON equality: 1 and true differ, key order does not matter.
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


class Validator:
    def __init__(self, schema: dict):
        self.root = schema

    def resolve(self, ref: str) -> dict:
        if not ref.startswith("#/"):
            raise ValueError(f"unsupported $ref {ref!r}; only local #/ references are allowed")
        node: object = self.root
        for part in ref[2:].split("/"):
            node = node[part]  # type: ignore[index]
        return node  # type: ignore[return-value]

    def errors(self, value: object, schema: dict, path: str = "$") -> list[str]:
        found: list[str] = []
        unknown = set(schema) - ANNOTATIONS - set(KEYWORDS)
        if unknown:
            raise ValueError(f"unsupported schema keyword(s) {sorted(unknown)} at {path}")
        for keyword, argument in schema.items():
            if keyword in KEYWORDS:
                found.extend(KEYWORDS[keyword](self, value, argument, schema, path))
        return found


def k_ref(v: Validator, value, ref, _schema, path):
    return v.errors(value, v.resolve(ref), path)


def k_type(_v, value, expected, _schema, path):
    names = expected if isinstance(expected, list) else [expected]
    if any(TYPES[name](value) for name in names):
        return []
    return [f"{path}: expected {' or '.join(names)}, got {type(value).__name__}"]


def k_const(_v, value, expected, _schema, path):
    return [] if _same(value, expected) else [f"{path}: must equal {expected!r}"]


def k_enum(_v, value, options, _schema, path):
    return [] if any(_same(value, option) for option in options) else [f"{path}: {value!r} not in {options!r}"]


def k_pattern(_v, value, pattern, _schema, path):
    if isinstance(value, str) and not re.search(pattern, value):
        return [f"{path}: {value!r} does not match {pattern!r}"]
    return []


def k_min_length(_v, value, minimum, _schema, path):
    return [f"{path}: shorter than {minimum}"] if isinstance(value, str) and len(value) < minimum else []


def k_minimum(_v, value, minimum, _schema, path):
    number = TYPES["number"](value)
    return [f"{path}: less than {minimum}"] if number and value < minimum else []


def k_min_items(_v, value, minimum, _schema, path):
    return [f"{path}: fewer than {minimum} items"] if isinstance(value, list) and len(value) < minimum else []


def k_unique_items(_v, value, unique, _schema, path):
    if unique and isinstance(value, list):
        seen = [json.dumps(item, sort_keys=True) for item in value]
        if len(seen) != len(set(seen)):
            return [f"{path}: items are not unique"]
    return []


def k_items(v: Validator, value, schema, _schema, path):
    if not isinstance(value, list):
        return []
    return [e for i, item in enumerate(value) for e in v.errors(item, schema, f"{path}[{i}]")]


def k_properties(v: Validator, value, properties, _schema, path):
    if not isinstance(value, dict):
        return []
    return [e for key, schema in properties.items() if key in value
            for e in v.errors(value[key], schema, f"{path}.{key}")]


def k_required(_v, value, required, _schema, path):
    if not isinstance(value, dict):
        return []
    return [f"{path}: missing required key {key!r}" for key in required if key not in value]


def k_additional(v: Validator, value, additional, schema, path):
    if not isinstance(value, dict):
        return []
    extra = [key for key in value if key not in schema.get("properties", {})]
    if additional is True:
        return []
    if additional is False:
        return [f"{path}: unexpected key {key!r}" for key in extra]
    return [e for key in extra for e in v.errors(value[key], additional, f"{path}.{key}")]


def k_property_names(v: Validator, value, schema, _schema, path):
    if not isinstance(value, dict):
        return []
    return [f"{path}: invalid key {key!r} ({e.split(': ', 1)[-1]})"
            for key in value for e in v.errors(key, schema, path)]


def k_min_properties(_v, value, minimum, _schema, path):
    return [f"{path}: fewer than {minimum} keys"] if isinstance(value, dict) and len(value) < minimum else []


KEYWORDS = {
    "$ref": k_ref, "type": k_type, "const": k_const, "enum": k_enum,
    "pattern": k_pattern, "minLength": k_min_length, "minimum": k_minimum,
    "minItems": k_min_items, "uniqueItems": k_unique_items, "items": k_items,
    "properties": k_properties, "required": k_required,
    "additionalProperties": k_additional, "propertyNames": k_property_names,
    "minProperties": k_min_properties,
}


def load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / f"{name}.schema.json").read_text(encoding="utf-8"))


def validate(data: object, schema_name: str) -> list[str]:
    schema = load_schema(schema_name)
    return Validator(schema).errors(data, schema)


def validate_file(path: Path, schema_name: str) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return [f"$: invalid JSON ({error})"]
    return validate(data, schema_name)


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--project", type=Path,
                        help="also validate PROJECT/.ai/apk.json and .ai/project.json when present")
    args = parser.parse_args()
    targets = [(ROOT / name, schema) for name, schema in KIT_FILES]
    if args.project:
        targets += [(args.project / name, schema) for name, schema in PROJECT_FILES
                    if (args.project / name).is_file()]
    failures = 0
    for path, schema in targets:
        errors = validate_file(path, schema)
        failures += bool(errors)
        for error in errors:
            print(f"schema {schema}: {path}: {error}")
    print(f"schemas: {'FAIL' if failures else 'PASS'} ({len(targets)} files)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
