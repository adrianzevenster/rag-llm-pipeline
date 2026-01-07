from __future__ import annotations

def chunk_text(text: str, chunk_size: int, overlap: int) -> list[tuple[int,int,str]]:
    text = text.strip()
    if not text:
        return []

    out = []
    i, n = 0, len(text)
    while i < n:
        j = min(i + chunk_size, n)

        # Prefer breaking on paragraph boundary
        k = text.rfind("\n\n", i, j)
        if k != -1 and k > i + int(chunk_size * 0.6):
            j = k

        chunk = text[i:j].strip()
        if chunk:
            out.append((i, j, chunk))

        if j >= n:
            break
        i = max(0, j - overlap)

    return out
