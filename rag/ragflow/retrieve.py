from __future__ import annotations

def retrieve(store, embedder, query: str, top_k: int) -> list[dict]:
    qv = embedder.embed([query])[0]
    res = store.search(qv, limit=top_k)
    out = []
    for r in res:
        p = r.payload or {}
        out.append({
            "score": float(r.score),
            "source_path": p.get("source_path"),
            "title": p.get("title"),
            "text": p.get("text"),
        })
    return out
