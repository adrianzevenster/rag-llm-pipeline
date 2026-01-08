from pydantic import BaseModel
import os
class Settings(BaseModel):
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    collection: str = "personal_knowledge"
    embedding_model: str = "nomic-ai/nomic-embed-text-v1.5"

    chunk_size: int = 900
    chunk_overlap: int = 150
    top_k: int = 8

    # If a PDF page yields less than this many characters, treat as “probably scanned”
    pdf_scanned_char_threshold: int = 50

settings = Settings()
