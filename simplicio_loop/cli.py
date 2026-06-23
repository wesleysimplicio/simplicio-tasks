"""CLI for simplicio-loop: install the bundled skills + hooks into a runtime."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from . import __version__

BUNDLE = Path(__file__).resolve().parent / "_bundle"


def _copy_tree(src: Path, dst: Path) -> int:
    """Copy every file under src into dst, preserving structure. Returns file count."""
    count = 0
    for item in src.rglob("*"):
        if item.is_file():
            out = dst / item.relative_to(src)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, out)
            count += 1
    return count


def install(target: Path, globally: bool) -> int:
    base = (Path.home() / ".claude") if globally else (target / ".claude")
    skills_dst = base / "skills"
    hooks_dst = (base / "hooks") if globally else (target / "hooks")

    if not (BUNDLE / "skills").is_dir():
        print("error: bundled skills not found in the installed package.", flush=True)
        return 1

    n_skills = _copy_tree(BUNDLE / "skills", skills_dst)
    n_hooks = _copy_tree(BUNDLE / "hooks", hooks_dst)

    print(f"simplicio-loop {__version__} installed:")
    print(f"  skills -> {skills_dst}  ({n_skills} files)")
    print(f"  hooks  -> {hooks_dst}  ({n_hooks} files)")
    print("")
    print("Use it in your agent runtime (Claude Code, Cursor, ...):")
    print("  /simplicio-tasks finish all the open issues")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="simplicio-loop",
        description=(
            "Install the simplicio-loop super-plugin (6 AI-orchestration skills + "
            "loop/token-economy hooks) into a runtime's skills location."
        ),
    )
    parser.add_argument(
        "command", nargs="?", default="install", choices=["install"],
        help="action to run (default: install)",
    )
    parser.add_argument(
        "--target", default=".",
        help="project directory to install into (default: current directory)",
    )
    parser.add_argument(
        "--global", dest="globally", action="store_true",
        help="install into ~/.claude instead of the project",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=f"simplicio-loop {__version__}",
    )
    args = parser.parse_args(argv)
    if args.command == "install":
        return install(Path(args.target).resolve(), args.globally)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
