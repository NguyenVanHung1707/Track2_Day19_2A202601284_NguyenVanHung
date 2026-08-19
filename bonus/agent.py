"""
HybridMemoryAgent — Bonus Challenge Lab 19.

Kết hợp Qdrant (vector memory) + Feast (feature memory) để tạo hệ thống
nhớ lai: remember() lưu văn bản + feature, recall() truy xuất bằng hybrid search.
"""
from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ── Lazy imports to avoid hard crashes if optional deps missing ──────────────
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance, VectorParams, PointStruct, Filter,
        FieldCondition, MatchValue, ScoredPoint,
    )
    _QDRANT_OK = True
except ImportError:
    _QDRANT_OK = False

try:
    from fastembed import TextEmbedding
    _EMBED_OK = True
except ImportError:
    _EMBED_OK = False

import numpy as np


@dataclass
class MemoryEntry:
    doc_id: str
    text: str
    metadata: dict = field(default_factory=dict)
    features: dict = field(default_factory=dict)


class HybridMemoryAgent:
    """Agentic memory combining vector (Qdrant) + feature (in-memory dict for demo)."""

    COLLECTION = "hybrid_memory"
    DIM = 384  # paraphrase-multilingual-MiniLM-L12-v2

    def __init__(self, qdrant_url: str = "http://localhost:6333",
                 in_memory: bool = False):
        if not _QDRANT_OK:
            raise RuntimeError("qdrant-client not installed. Run: pip install qdrant-client")
        if not _EMBED_OK:
            raise RuntimeError("fastembed not installed. Run: pip install fastembed")

        # Try remote first; fall back to :memory: if server not available
        if in_memory:
            self._client = QdrantClient(":memory:")
        else:
            try:
                self._client = QdrantClient(url=qdrant_url, timeout=2)
                self._client.get_collections()  # probe
            except Exception:
                print("[HybridMemoryAgent] Qdrant server not available — using :memory: mode")
                self._client = QdrantClient(":memory:")

        self._embedder = TextEmbedding("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        self._feature_store: dict[str, dict] = {}  # user_id -> features
        self._bm25_index: dict[str, list[str]] = {}  # doc_id -> tokens

        # Ensure collection exists
        existing = [c.name for c in self._client.get_collections().collections]
        if self.COLLECTION not in existing:
            self._client.create_collection(
                collection_name=self.COLLECTION,
                vectors_config=VectorParams(size=self.DIM, distance=Distance.COSINE),
            )

    # ── Write ────────────────────────────────────────────────────────────────
    def remember(self, text: str, metadata: dict | None = None,
                 user_features: dict | None = None) -> str:
        """Store a document in vector memory + feature memory.

        Args:
            text: The text content to remember.
            metadata: Optional payload (topic, source, …).
            user_features: Optional user-level features to associate.

        Returns:
            doc_id: The unique ID assigned to this memory.
        """
        doc_id = str(uuid.uuid4())  # full UUID required by in-memory Qdrant
        meta = metadata or {}
        feats = user_features or {}

        # 1. Embed & upsert into Qdrant
        vec = list(self._embedder.embed([text]))[0].tolist()
        self._client.upsert(
            collection_name=self.COLLECTION,
            points=[PointStruct(id=doc_id, vector=vec, payload={**meta, "text": text})],
        )

        # 2. BM25 index (simple token bag)
        self._bm25_index[doc_id] = text.lower().split()

        # 3. Feature store (in-memory for demo; swap Feast in production)
        uid = meta.get("user_id", "anon")
        if uid not in self._feature_store:
            self._feature_store[uid] = {}
        self._feature_store[uid].update(feats)
        self._feature_store[uid]["last_remembered"] = time.time()
        self._feature_store[uid].setdefault("memory_count", 0)
        self._feature_store[uid]["memory_count"] += 1

        return doc_id

    # ── Read ─────────────────────────────────────────────────────────────────
    def recall(self, query: str, top_k: int = 5,
               user_id: str | None = None,
               topic_filter: str | None = None) -> list[MemoryEntry]:
        """Retrieve memories using hybrid (vector + BM25) search with RRF fusion.

        Args:
            query: Natural language query.
            top_k: Number of results to return.
            user_id: If given, attach user features to results.
            topic_filter: If given, filter by topic metadata field.

        Returns:
            List of MemoryEntry sorted by hybrid relevance score.
        """
        k = top_k * 5  # over-fetch for RRF

        # 1. Vector search
        vec = list(self._embedder.embed([query]))[0].tolist()
        vec_filter = None
        if topic_filter:
            vec_filter = Filter(
                must=[FieldCondition(key="topic", match=MatchValue(value=topic_filter))]
            )
        result = self._client.query_points(
            collection_name=self.COLLECTION,
            query=vec,
            limit=k,
            query_filter=vec_filter,
        )
        vec_hits = result.points

        # 2. BM25 (naive TF scoring for demo)
        q_tokens = set(query.lower().split())
        bm25_scores: dict[str, float] = {}
        for doc_id, tokens in self._bm25_index.items():
            score = sum(tokens.count(t) for t in q_tokens) / (len(tokens) + 1)
            bm25_scores[doc_id] = score
        bm25_ranked = sorted(bm25_scores, key=bm25_scores.get, reverse=True)[:k]

        # 3. RRF fusion
        rrf_scores: dict[str, float] = {}
        for rank, hit in enumerate(vec_hits, 1):
            rrf_scores[hit.id] = rrf_scores.get(hit.id, 0) + 1 / (60 + rank)
        for rank, doc_id in enumerate(bm25_ranked, 1):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (60 + rank)

        top_ids = sorted(rrf_scores, key=rrf_scores.get, reverse=True)[:top_k]

        # 4. Fetch payloads & attach features
        user_feats = self._feature_store.get(user_id or "anon", {})
        results = []
        for doc_id in top_ids:
            hits = self._client.retrieve(
                collection_name=self.COLLECTION,
                ids=[doc_id],
                with_payload=True,
            )
            if not hits:
                continue
            payload = hits[0].payload or {}
            results.append(MemoryEntry(
                doc_id=doc_id,
                text=payload.get("text", ""),
                metadata={k: v for k, v in payload.items() if k != "text"},
                features=user_feats,
            ))

        return results

    # ── Utility ──────────────────────────────────────────────────────────────
    def build_context(self, entries: list[MemoryEntry]) -> str:
        """Assemble retrieved memories into an LLM-ready context string."""
        lines = ["=== HYBRID MEMORY CONTEXT ===\n"]
        for i, e in enumerate(entries, 1):
            lines.append(f"[{i}] doc_id={e.doc_id}")
            lines.append(f"    text   : {e.text[:120]}")
            if e.metadata:
                lines.append(f"    meta   : {e.metadata}")
            if e.features:
                lines.append(f"    feats  : {e.features}")
            lines.append("")
        return "\n".join(lines)

    def count(self) -> int:
        """Return number of stored memories."""
        return self._client.count(self.COLLECTION).count
