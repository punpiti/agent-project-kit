#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  echo "Usage: $0 input.md [output.pdf]" >&2
  exit 2
fi

input="$1"
output="${2:-${input%.*}.pdf}"
template_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

pandoc "$input" \
  --defaults="$template_dir/thai-a4-defaults.yaml" \
  --resource-path=".:$template_dir:$(dirname "$input")" \
  -o "$output"
