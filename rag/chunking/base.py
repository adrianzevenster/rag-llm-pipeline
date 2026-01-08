from __future__ import annotations
import re

_REF_HEADER_RE = re.compile(r"^\s*(references|bibliography|works cited)\s*$", re.IGNORECASE | re.MULTILINE)

def chunk_text(text: str, chunk_size: int, overlap: int) -> list[tuple[int,int,str]]:
    text = text.strip()
    if not text:
        return []

    out = []
    i, n = 0, len(text)

    ref_start = None
    m = _REF_HEADER_RE.search(text)
    if m:
        ref_start = m.start()
    ref_chunks_allowed = 3
    ref_chunks_used = 0

    while i < n:
        j = min(i + chunk_size, n)
        k = text.rfind("\n\n", i, j)
        if k != -1 and k > i + int(chunk_size * 0.6):
            j = k

        chunk = text[i:j].strip()
        if chunk:
            if ref_start is not None and i >= ref_start:
                if ref_chunks_used >= ref_chunks_allowed:
                    break
                ref_chunks_used += 1

            out.append((i, j, chunk))

        if j >= n:
            break
        i = max(0, j - overlap)

    return out
