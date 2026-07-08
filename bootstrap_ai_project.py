#!/usr/bin/env python3
from pathlib import Path
import runpy

script = Path(__file__).resolve().parent / "scripts" / "bootstrap_ai_project.py"
runpy.run_path(str(script), run_name="__main__")
