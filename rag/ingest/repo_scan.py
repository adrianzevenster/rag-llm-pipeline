from __future__ import annotations
from pathlib import Path
from pathspec import PathSpec

DEFAULT_EXCLUDES = [
    ".git/**", ".venv/**", "venv/**", "__pycache__/**", "node_modules/**",
    "dist/**", "build/**", ".pytest_cache/**",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.mp4", "*.mov", "*.zip", "*.tar", "*.gz",
    "*.whl", "*.so", "*.dll", "*.exe", "*.bin"
]

def load_gitignore(root: Path) -> PathSpec | None:
    gi = root / ".gitignore"
    if not gi.exists():
        return None
    lines = gi.read_text(errors="ignore").splitlines()
    return PathSpec.from_lines("gitwildmatch", lines)

def iter_files(root: Path):
    root = root.resolve()
    gi_spec = load_gitignore(root)
    default_spec = PathSpec.from_lines("gitwildmatch", DEFAULT_EXCLUDES)

    for p in root.rglob("*"):
        if p.is_dir():
            continue
        rel = p.relative_to(root).as_posix()

        if default_spec.match_file(rel):
            continue
        if gi_spec and gi_spec.match_file(rel):
            continue

        yield p
