from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import json


# Common text-like extensions (you can extend this list as needed)
TEXT_EXTS = {
    ".txt", ".md", ".rst", ".log", ".csv",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".py", ".ipynb", ".js", ".ts", ".tsx", ".jsx",
    ".java", ".go", ".rs", ".c", ".cpp", ".h", ".hpp",
    ".sql", ".sh", ".bash", ".zsh",
    ".dockerfile", ".env",
}


@dataclass
class TextLoadResult:
    text: str
    encoding: str
    bytes_read: int


def _try_decode(raw: bytes) -> Optional[tuple[str, str]]:
    """
    Try a small set of encodings commonly encountered in repos and documents.
    Returns (decoded_text, encoding) or None if all fail.
    """
    candidates = ["utf-8", "utf-16", "utf-16le", "utf-16be", "latin-1"]
    for enc in candidates:
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return None


def _sanitize_text(s: str) -> str:
    """
    Make text safe for chunking + embedding:
    - remove null bytes
    - normalize newlines
    - remove most control chars (keep \n, \t)
    """
    s = s.replace("\x00", "")
    s = s.replace("\r\n", "\n").replace("\r", "\n")

    cleaned = []
    for ch in s:
        o = ord(ch)
        # Keep printable, newline, tab
        if ch in ("\n", "\t") or o >= 32:
            cleaned.append(ch)
    return "".join(cleaned).strip()


def _summarize_json_keys(obj, max_keys: int = 50) -> str:
    """
    Small helper for JSON: list top-level keys (useful context for LLM).
    """
    if isinstance(obj, dict):
        keys = list(obj.keys())[:max_keys]
        more = "" if len(obj.keys()) <= max_keys else f" (+{len(obj.keys())-max_keys} more)"
        return "Top-level keys: " + ", ".join(map(str, keys)) + more
    if isinstance(obj, list):
        return f"Top-level is a list of length {len(obj)}"
    return f"Top-level type: {type(obj).__name__}"


def load_text_file(
        path: Path,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB safety cap
) -> TextLoadResult:
    """
    Load a text-like file robustly. Will read up to max_bytes.
    """
    raw = path.read_bytes()
    if len(raw) > max_bytes:
        raw = raw[:max_bytes]

    decoded = _try_decode(raw)
    if decoded is None:
        # Last resort: replace errors with placeholders using utf-8
        text = raw.decode("utf-8", errors="replace")
        enc = "utf-8(errors=replace)"
    else:
        text, enc = decoded

    text = _sanitize_text(text)
    return TextLoadResult(text=text, encoding=enc, bytes_read=len(raw))


def render_text_with_header(path: Path, text: str, encoding: str) -> str:
    """
    Adds a small header (file metadata + structure hints).
    This helps the model attribute context correctly.
    """
    suffix = path.suffix.lower()
    header_lines = [
        f"FILE: {path.name}",
        f"PATH: {path.resolve()}",
        f"TYPE: {suffix or '(no extension)'}",
        f"ENCODING: {encoding}",
    ]

    # Special handling: Jupyter notebooks are JSON; extract cell sources if possible
    if suffix == ".ipynb":
        try:
            nb = json.loads(text)
            cells = nb.get("cells", [])
            out = []
            for c in cells:
                if c.get("cell_type") in ("code", "markdown"):
                    src = c.get("source", [])
                    if isinstance(src, list):
                        src = "".join(src)
                    out.append(f"## CELL ({c.get('cell_type')})\n{src}".strip())
            body = "\n\n".join(out).strip()
            header_lines.append(f"NOTEBOOK_CELLS: {len(cells)}")
            return "\n".join(header_lines) + "\n\n" + (body or text)
        except Exception:
            header_lines.append("NOTEBOOK_PARSE: failed (kept raw text)")
            return "\n".join(header_lines) + "\n\n" + text

    # Special handling: JSON files – add key summary if parseable
    if suffix == ".json":
        try:
            obj = json.loads(text)
            header_lines.append("JSON: " + _summarize_json_keys(obj))
        except Exception:
            header_lines.append("JSON: parse failed")

    return "\n".join(header_lines) + "\n\n" + text


def load_text_like(path: Path) -> str:
    """
    Convenience function used by loaders.py:
    returns final text ready for chunking + embedding.
    """
    res = load_text_file(path)
    return render_text_with_header(path, res.text, res.encoding)
