# -*- coding: utf-8 -*-
"""
LLMWare Local RAG Engine for ReaperOS.
Zero-latency, offline semantic indexing and vector retrieval on macOS.
"""

import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

class LocalRAGEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model = SentenceTransformer(model_name)
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: List[np.ndarray] = []

    def index_document(self, doc_id: str, content: str) -> None:
        """Splits content into paragraphs, computes embeddings, and stores them."""
        chunks = [p.strip() for p in content.split("\n\n") if p.strip()]
        for chunk in chunks:
            emb = self.model.encode(chunk)
            self.documents.append({
                "doc_id": doc_id,
                "text": chunk
            })
            self.embeddings.append(emb)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Finds top-k most semantically relevant document chunks."""
        if not self.embeddings:
            return []

        query_emb = self.model.encode(query)
        
        # Calculate cosine similarity
        similarities = []
        for emb in self.embeddings:
            dot_product = np.dot(query_emb, emb)
            norm_q = np.linalg.norm(query_emb)
            norm_e = np.linalg.norm(emb)
            similarity = dot_product / (norm_q * norm_e) if norm_q > 0 and norm_e > 0 else 0.0
            similarities.append(similarity)

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "doc_id": self.documents[idx]["doc_id"],
                "text": self.documents[idx]["text"],
                "score": float(similarities[idx])
            })
        return results
