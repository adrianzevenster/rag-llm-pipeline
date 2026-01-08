from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer


class NomicEmbedder:
    def __init__(self, model_name: str):
        # Nomic's embed models rely on custom HF code
        self.model = SentenceTransformer(model_name, trust_remote_code=True)

    @property
    def dim(self) -> int:
        return int(self.model.get_sentence_embedding_dimension())

    def embed(self, texts: list[str]) -> np.ndarray:
        v = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(v, dtype="float32")
