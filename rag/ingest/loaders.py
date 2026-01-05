from __future__ import annotations
from pathlib import Path
from rag.ingest.pdf import extract_pdf_text
from rag.ingest.office import extract_docx_text, extract_pptx_text
from rag.ingest.tabular import extract_excel_text
from rag.ingest.text import load_text_like

TEXT_EXTS = {".txt", ".md", ".rst", ".py", ".js", ".ts", ".java", ".go", ".sql", ".yaml", ".yml", ".json", ".ipynb"}

def load_any(path: Path) -> str | None:
    suf = path.suffix.lower()

    if suf == ".pdf":
        return extract_pdf_text(path)
    if suf == ".docx":
        return extract_docx_text(path)
    if suf == ".pptx":
        return extract_pptx_text(path)
    if suf in [".xlsx", ".xls"]:
        return extract_excel_text(path)
    if suf in TEXT_EXTS:
        return load_text_like(path)

    return None
