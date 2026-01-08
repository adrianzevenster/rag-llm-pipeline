# rag/ragflow/prompt.py
from __future__ import annotations

import re

_AUTHOR_QUERY_RE = re.compile(
    r"\b(my|i)\b.*\b(papers?|publications?|articles?|thesis|report|reports)\b|\bpapers?\s+i\s+have\s+written\b",
    re.IGNORECASE,
)

_REF_HEADER_RE = re.compile(r"^\s*(references|bibliography|works cited)\s*$", re.IGNORECASE | re.MULTILINE)

def _is_author_query(question: str) -> bool:
    return bool(_AUTHOR_QUERY_RE.search(question.strip()))

def _looks_like_reference_chunk(text: str) -> bool:
    # Heuristic: reference sections often have a References header or lots of year-citations.
    if _REF_HEADER_RE.search(text):
        return True
    year_hits = len(re.findall(r"\b(19|20)\d{2}\b", text))
    doi_hits = len(re.findall(r"\bdoi:\s*", text, flags=re.IGNORECASE))
    # If a short chunk has many years/doi patterns, it's probably bibliographic.
    return (year_hits >= 6) or (doi_hits >= 2)


_AUTHOR_NAME_RE = re.compile(
    r"\bAdrian\s+C\.?\s+Zevenster\b", re.IGNORECASE
)

def _is_author_evidence_chunk(text: str) -> bool:
    # Explicit author-name hit
    if _AUTHOR_NAME_RE.search(text):
        return True

    # Title-page style signals
    title_page_markers = [
        "submitted by",
        "author:",
        "by ",
        "university",
        "department",
        "date",
    ]
    lowered = text.lower()
    return any(m in lowered for m in title_page_markers)


def build_prompt(question: str, contexts: list[dict]) -> str:
    # Light filtering only for author/publication-type questions:
    # keep non-reference-like chunks first, but don't drop everything.
    if _is_author_query(question) and contexts:
        author_hits = []
    neutral = []
    refs = []

    for c in contexts:
        text = c.get("text", "")
        if _is_author_evidence_chunk(text):
            author_hits.append(c)
        elif _looks_like_reference_chunk(text):
            refs.append(c)
        else:
            neutral.append(c)

    # Order matters: authorship evidence first
    contexts = author_hits + neutral + refs


    blocks = []
    for i, c in enumerate(contexts, start=1):
        blocks.append(
            f"[{i}] {c.get('source_path')} | {c.get('title')}\n{c.get('text')}\n"
        )
    ctx = "\n".join(blocks) if blocks else "NO_CONTEXT"

    if _is_author_query(question):
        # Specialized instruction to prevent "references == authored papers"
        rules = """You are a careful assistant.
Use ONLY the provided context to answer.

CRITICAL RULES for "papers I have written / my publications":
- Do NOT treat citations in a References/Bibliography section as papers authored by the user.
- Only list a paper/report as "written by the user" if the context explicitly indicates authorship
  (e.g., title page shows an author name, "by <name>", "Author:", "Submitted by", or similar).
- If authorship is not explicitly present, say you cannot confirm authorship from the indexed text.
- In that case, list the most likely candidate documents (filenames) and quote the exact lines that suggest authorship,
  OR say what is missing (e.g., title page/author field not captured in extracted text).

Cite sources using [1], [2], etc.
"""
    else:
        rules = """You are a careful assistant.
Use ONLY the provided context to answer. If context is insufficient, say exactly what is missing.
Cite sources using [1], [2], etc.
"""

    return f"""{rules}

Question:
{question}

Context:
{ctx}

Answer (with citations):
"""
