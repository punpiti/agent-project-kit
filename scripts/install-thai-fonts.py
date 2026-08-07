#!/usr/bin/env python3
"""Install required Thai fonts to a user-local font directory.

Google Sarabun is downloaded from an immutable Google Fonts revision only when
--allow-download is supplied. TH Sarabun New is installed only from a caller-
provided source directory; the package does not redistribute Windows font files.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import urllib.request


GOOGLE_FONTS_REVISION = "c28e08582e7bd36751febb3391142a5eb18bbb34"
SARABUN_FILES = (
    "Sarabun-Thin.ttf",
    "Sarabun-ThinItalic.ttf",
    "Sarabun-ExtraLight.ttf",
    "Sarabun-ExtraLightItalic.ttf",
    "Sarabun-Light.ttf",
    "Sarabun-LightItalic.ttf",
    "Sarabun-Regular.ttf",
    "Sarabun-Italic.ttf",
    "Sarabun-Medium.ttf",
    "Sarabun-MediumItalic.ttf",
    "Sarabun-SemiBold.ttf",
    "Sarabun-SemiBoldItalic.ttf",
    "Sarabun-Bold.ttf",
    "Sarabun-BoldItalic.ttf",
    "Sarabun-ExtraBold.ttf",
    "Sarabun-ExtraBoldItalic.ttf",
    "OFL.txt",
)
SARABUN_BASE_URL = (
    "https://raw.githubusercontent.com/google/fonts/"
    f"{GOOGLE_FONTS_REVISION}/ofl/sarabun"
)


def default_target() -> Path:
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Fonts"
    return Path.home() / ".local" / "share" / "fonts"


def font_available(family: str) -> bool:
    executable = shutil.which("fc-list")
    if not executable:
        return False
    result = subprocess.run(
        [executable, ":", "family"],
        check=False,
        capture_output=True,
        text=True,
    )
    return family.casefold() in result.stdout.casefold()


def copy_file(source: Path, target: Path, *, force: bool, dry_run: bool) -> None:
    destination = target / source.name
    if destination.exists() and not force:
        print(f"exists: {destination}")
        return
    print(f"install: {source} -> {destination}")
    if not dry_run:
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def install_sarabun(target: Path, *, allow_download: bool, force: bool, dry_run: bool) -> None:
    if font_available("Sarabun") and not force:
        print("available: Google Sarabun")
        return
    if not allow_download:
        raise SystemExit(
            "Google Sarabun is missing. This installation downloads 16 font files "
            "plus the OFL license from Google Fonts. Review metered-network cost, "
            "then rerun with --allow-download."
        )
    if dry_run:
        for name in SARABUN_FILES:
            print(f"download: {SARABUN_BASE_URL}/{name} -> {target / name}")
        return
    with tempfile.TemporaryDirectory(prefix="apk-sarabun-") as temp_name:
        temp = Path(temp_name)
        for name in SARABUN_FILES:
            url = f"{SARABUN_BASE_URL}/{name}"
            print(f"download: {url}")
            urllib.request.urlretrieve(url, temp / name)
        target.mkdir(parents=True, exist_ok=True)
        for name in SARABUN_FILES:
            copy_file(temp / name, target, force=force, dry_run=False)


def install_th_sarabun_new(
    target: Path, source_dir: Path | None, *, force: bool, dry_run: bool
) -> None:
    if font_available("TH Sarabun New") and not force:
        print("available: TH Sarabun New")
        return
    if source_dir is None:
        raise SystemExit(
            "TH Sarabun New is missing. Supply a legally obtained font directory "
            "with --th-sarabun-source. This package does not redistribute or "
            "automatically download TH Sarabun New."
        )
    if not source_dir.is_dir():
        raise SystemExit(f"TH Sarabun New source directory not found: {source_dir}")
    matches = [
        path
        for path in source_dir.iterdir()
        if path.is_file()
        and path.suffix.casefold() in {".ttf", ".otf"}
        and "thsarabunnew" in "".join(ch for ch in path.stem.casefold() if ch.isalnum())
    ]
    if not matches:
        raise SystemExit(f"No TH Sarabun New font files found in: {source_dir}")
    for source in sorted(matches):
        copy_file(source, target, force=force, dry_run=dry_run)


def refresh_cache(dry_run: bool) -> None:
    executable = shutil.which("fc-cache")
    if not executable:
        print("warning: fc-cache is unavailable; verify fonts with the platform font manager")
        return
    print("refresh: fontconfig cache")
    if not dry_run:
        subprocess.run([executable, "-f"], check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--font",
        choices=("sarabun", "th-sarabun-new", "all"),
        default="all",
    )
    parser.add_argument("--target", type=Path, default=default_target())
    parser.add_argument("--th-sarabun-source", type=Path)
    parser.add_argument(
        "--allow-download",
        action="store_true",
        help="confirm that network cost was reviewed and allow Google Sarabun downloads",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.font in {"sarabun", "all"}:
        install_sarabun(
            args.target,
            allow_download=args.allow_download,
            force=args.force,
            dry_run=args.dry_run,
        )
    if args.font in {"th-sarabun-new", "all"}:
        install_th_sarabun_new(
            args.target,
            args.th_sarabun_source,
            force=args.force,
            dry_run=args.dry_run,
        )
    refresh_cache(args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
