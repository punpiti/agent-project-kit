# OneDrive Env Cleanup Log

Date: 2026-07-06

Env paths moved out of OneDrive and into local quarantine:

- `KU/president/.venv`
- `software/auto-ungrayscale/.venv`
- `urban/urban_platform/.venv`
- `แนะแนว/.venv-pptx`

Notes:

- No `conda-meta` trees were found in the current sweep.
- `KU/president`, `software/auto-ungrayscale`, `urban/urban_platform`, and `แนะแนว` all keep local metadata or project notes, so the envs can be recreated outside OneDrive from the committed requirements or project instructions.
- A separate I/O error surfaced at `nowcast/docs/FF 2567/สถานะแผน` during directory traversal. That path was not modified.

Restore hints:

- `KU/president`: `python -m pip install -r requirements.txt`
- `software/auto-ungrayscale`: `python -m pip install -r requirements.txt`
- `urban/urban_platform`: `python -m pip install -r requirements.txt`
- `แนะแนว`: recreate a local tool env from the project-specific workflow that uses `python-pptx` tooling, if needed.
