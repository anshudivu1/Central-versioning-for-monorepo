"""
inject_version.py
-----------------
Build-time version injection script.

Reads the authoritative version from workspace.yml at the repo root,
then walks every package directory looking for pyproject.toml files.
For each file it:
  1. Asserts the current version is the sentinel (0.0.0.dev0).
  2. Replaces the sentinel with the release version.
  3. Rewrites the file in-place (build workspace only, never source control).

Usage:
    python versioning/inject_version.py

The script is zero-dependency (stdlib only) so it runs in any CI environment
without installing additional packages.
"""

import re
import sys
from pathlib import Path

SENTINEL = "0.0.0.dev0"
REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_FILE = REPO_ROOT / "workspace.yml"
PACKAGES_DIR = REPO_ROOT / "packages"


def read_release_version() -> str:
    """Parse the version string from workspace.yml."""
    content = WORKSPACE_FILE.read_text(encoding="utf-8")
    match = re.search(r'^version:\s*["\']?([^"\'\s]+)["\']?', content, re.MULTILINE)
    if not match:
        print(f"ERROR: Could not find 'version' key in {WORKSPACE_FILE}", file=sys.stderr)
        sys.exit(1)
    return match.group(1)


def find_pyproject_files():
    """Yield all pyproject.toml paths inside the packages directory."""
    return sorted(PACKAGES_DIR.glob("*/pyproject.toml"))


def inject(pyproject_path: Path, release_version: str) -> None:
    """Replace the sentinel version with release_version in a pyproject.toml."""
    content = pyproject_path.read_text(encoding="utf-8")

    if SENTINEL not in content:
        print(
            f"  SKIP  {pyproject_path.parent.name}: sentinel '{SENTINEL}' not found "
            f"(already injected or non-standard version present)"
        )
        return

    updated = content.replace(f'version = "{SENTINEL}"', f'version = "{release_version}"')
    pyproject_path.write_text(updated, encoding="utf-8")
    print(f"  OK    {pyproject_path.parent.name}: {SENTINEL} -> {release_version}")


def main() -> None:
    release_version = read_release_version()
    print(f"Release version read from workspace.yml: {release_version}")
    print(f"Scanning packages in: {PACKAGES_DIR}\n")

    pyproject_files = find_pyproject_files()
    if not pyproject_files:
        print("ERROR: No pyproject.toml files found under packages/", file=sys.stderr)
        sys.exit(1)

    for path in pyproject_files:
        inject(path, release_version)

    print(f"\nDone. {len(pyproject_files)} package(s) processed.")


if __name__ == "__main__":
    main()
