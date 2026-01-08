from __future__ import annotations
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
import numpy as np

class QdrantStore:
    def __init__(self, url: str, collection: str, dim: int):
        self.client = QdrantClient(url=url)
        self.collection = collection
        self._ensure_collection(dim)

    def _ensure_collection(self, dim: int):
        existing = {c.name for c in self.client.get_collections().collections}
        if self.collection in existing:
            return
        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=qm.VectorParams(size=dim, distance=qm.Distance.COSINE),
        )

    def upsert(self, ids: list[str], vectors: np.ndarray, payloads: list[dict]):
        self.client.upsert(
            collection_name=self.collection,
            points=qm.Batch(ids=ids, vectors=vectors.tolist(), payloads=payloads),
        )

    def search(self, query_vec: np.ndarray, limit: int):
        return self.client.search(
            collection_name=self.collection,
            query_vector=query_vec.tolist(),
            limit=limit,
        )
