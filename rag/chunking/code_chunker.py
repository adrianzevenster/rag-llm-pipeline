from __future__ import annotations
import re

DEF_RE = re.compile(r"^(def |class |function |public |private |protected |\w+\s+\w+\s*\()", re.MULTILINE)

def chunk_code(text: str, max_chars: int = 1200) -> list[str]:
    text = text.strip()
    if not text:
        return []

    starts = [m.start() for m in DEF_RE.finditer(text)]
    if not starts:
        # fallback: simple slicing
        return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]

    starts = [0] + sorted(set(starts))
    chunks = []
    for idx, s in enumerate(starts):
        e = starts[idx + 1] if idx + 1 < len(starts) else len(text)
        block = text[s:e].strip()
        if not block:
            continue

        # if block is huge, slice it
        if len(block) > max_chars:
            chunks.extend([block[i:i+max_chars] for i in range(0, len(block), max_chars)])
        else:
            chunks.append(block)
    return chunks
