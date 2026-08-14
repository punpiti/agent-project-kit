# Benchmark report validation

Generated from `benchmarks/results/latest.json` on 2026-08-13.

Portable-artifact delivery result:

- artifact validation: passed
- HTML packaging: passed
- structural verification: passed
- blocks: 14
- KPI cards: 4
- charts: 1
- tables: 1
- browser interaction and source-dialog verification: not run

The delivery builder could not find a local Chromium headless executable and,
by design, did not download one. Treat `report.html` as structurally validated,
not browser-QA-complete. Run the same delivery command with
`CHROMIUM_EXECUTABLE_PATH` set before the Marketplace release if full render
and interaction verification is required.
