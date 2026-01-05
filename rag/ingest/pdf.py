from __future__ import annotations
from pathlib import Path
import pdfplumber
from pypdf import PdfReader

def extract_pdf_text(path: Path) -> str:
    texts = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text() or ""
                if t.strip():
                    texts.append(t)
    except Exception:
        texts = []

    if not texts:
        try:
            r = PdfReader(str(path))
            for pg in r.pages:
                t = (pg.extract_text() or "").strip()
                if t:
                    texts.append(t)
        except Exception:
            return ""

    return "\n\n".join(texts).strip()
