"""
demo.py — Minh họa 5 loại câu hỏi khác nhau với HybridMemoryAgent.

Chạy: python bonus/demo.py
Output: assembled context cho 5 queries, exit code 0 nếu thành công.
"""
import sys
from pathlib import Path

# Thêm thư mục gốc vào path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bonus.agent import HybridMemoryAgent


def seed_memories(agent: HybridMemoryAgent):
    """Nạp 10 văn bản mẫu vào bộ nhớ."""
    docs = [
        ("Qdrant là vector database mã nguồn mở, hỗ trợ ANN với HNSW index.",
         {"topic": "vector_db", "lang": "vi"}, {"u_001": {"expertise": "infra"}}),
        ("Feast là feature store giúp quản lý feature cho ML, tránh leakage.",
         {"topic": "feature_store", "lang": "vi"}, {"u_001": {"expertise": "mlops"}}),
        ("BM25 là thuật toán ranking từ khóa dựa trên TF-IDF cải tiến.",
         {"topic": "search", "lang": "vi"}, {}),
        ("Hybrid search kết hợp BM25 và vector search qua RRF fusion.",
         {"topic": "search", "lang": "vi"}, {}),
        ("Point-in-time join tránh data leakage khi huấn luyện mô hình ML.",
         {"topic": "feature_store", "lang": "vi"}, {"u_002": {"expertise": "ml"}}),
        ("On-demand feature view tính feature tại request time, không pre-compute.",
         {"topic": "feature_store", "lang": "vi"}, {}),
        ("Semantic cache dùng cosine similarity để tái sử dụng kết quả truy vấn.",
         {"topic": "cache", "lang": "vi"}, {}),
        ("Multi-tenant security dùng namespace prefix để cô lập dữ liệu tenant.",
         {"topic": "security", "lang": "vi"}, {}),
        ("Filtered ANN duy trì recall=1.0 khi filter hẹp, post-filter thì không.",
         {"topic": "vector_db", "lang": "vi"}, {}),
        ("Agentic retrieval dùng reflection để mở rộng query động theo kết quả.",
         {"topic": "agent", "lang": "vi"}, {}),
    ]
    for text, meta, feats in docs:
        uid = list(feats.keys())[0] if feats else None
        user_features = list(feats.values())[0] if feats else {}
        if uid:
            meta["user_id"] = uid
        agent.remember(text, metadata=meta, user_features=user_features)
    print(f"✅ Đã lưu {agent.count()} memories vào Qdrant\n")


def run_demo(agent: HybridMemoryAgent):
    """Chạy 5 loại câu hỏi khác nhau."""

    queries = [
        # (type, query, user_id, topic_filter)
        ("1. Exact keyword",
         "Qdrant HNSW index ANN", "u_001", None),
        ("2. Paraphrase/Semantic",
         "Làm sao tránh rò rỉ dữ liệu khi train model?", "u_002", None),
        ("3. Mixed (keyword + semantic)",
         "hybrid search vector BM25 recall", None, None),
        ("4. Filtered by topic",
         "cách quản lý feature", None, "feature_store"),
        ("5. Tiếng Việt có code-switching",
         "semantic cache dùng cosine similarity để save latency", None, None),
    ]

    all_passed = True
    for label, query, user_id, topic_filter in queries:
        print(f"{'─'*60}")
        print(f"📌 {label}")
        print(f"   Query: \"{query}\"")
        if topic_filter:
            print(f"   Filter: topic={topic_filter}")
        try:
            results = agent.recall(query, top_k=3,
                                   user_id=user_id,
                                   topic_filter=topic_filter)
            context = agent.build_context(results)
            print(context)
            print(f"   → Trả về {len(results)} kết quả ✅")
        except Exception as e:
            print(f"   ❌ Lỗi: {e}")
            all_passed = False

    print("═"*60)
    if all_passed:
        print("🎉 Demo hoàn thành thành công! Tất cả 5 loại query đã pass.")
        return 0
    else:
        print("⚠️  Một số query thất bại.")
        return 1


def main():
    print("=" * 60)
    print("HybridMemoryAgent — Bonus Demo (Lab 19)")
    print("=" * 60)
    print()

    # Auto-fallback: tries localhost:6333, falls back to :memory:
    agent = HybridMemoryAgent()

    # Reset collection for fresh demo
    try:
        agent._client.delete_collection(agent.COLLECTION)
        from qdrant_client.models import Distance, VectorParams
        agent._client.create_collection(
            collection_name=agent.COLLECTION,
            vectors_config=VectorParams(size=agent.DIM, distance=Distance.COSINE),
        )
    except Exception:
        pass

    seed_memories(agent)
    exit_code = run_demo(agent)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
