# Kiến trúc Hệ thống AI Memory: HybridMemoryAgent

> **Tác giả:** Nguyễn Văn Hưng — Lab 19 Bonus Challenge  
> **Ngày:** 2026-08-19  
> **Từ:** ≈ 650 từ

---

## 1. Tổng quan

HybridMemoryAgent là hệ thống truy xuất thông tin thế hệ mới kết hợp **Vector Store** (Qdrant) cho truy xuất ngữ nghĩa và **Feature Store** (Feast) cho đặc trưng người dùng theo thời gian thực. Hệ thống hỗ trợ cả tiếng Anh lẫn tiếng Việt, xử lý tốt hiện tượng code-switching (xen tiếng Anh-Việt) — vấn đề đặc thù trong bối cảnh Việt Nam.

---

## 2. Sơ đồ kiến trúc

```
┌──────────────────────────────────────────────────────────┐
│                     HybridMemoryAgent                    │
│                                                          │
│  ┌──────────┐    ┌───────────────┐    ┌───────────────┐  │
│  │ remember │    │  Embed (fastembed)  │    │ Feast Write   │  │
│  │ (write)  │───▶│  + BM25 index │───▶│ (materialize) │  │
│  └──────────┘    └───────────────┘    └───────────────┘  │
│                         │                     │           │
│                    Qdrant                  SQLite         │
│                   (vectors)              (features)       │
│                         │                     │           │
│  ┌──────────┐    ┌───────────────┐    ┌───────────────┐  │
│  │  recall  │    │ Hybrid Search │    │ Feast Online  │  │
│  │  (read)  │───▶│ (RRF fusion)  │◀───│  get_online   │  │
│  └──────────┘    └───────────────┘    └───────────────┘  │
│                         │                                 │
│                  Context Assembly                         │
│              (doc_ids + user features)                    │
└──────────────────────────────────────────────────────────┘
```

---

## 3. Ba quyết định kiến trúc & Tradeoff

### 3.1 Chunking Strategy — Fixed-size vs Semantic Chunking

**Quyết định:** Dùng **fixed-size chunking (512 tokens, overlap 64 tokens)** thay vì semantic chunking.

**Lý do:** Với tài liệu tiếng Việt có nhiều câu ngắn và code-switching, mô hình phân đoạn ngữ nghĩa (như `nltk.sent_tokenize`) hay bị lỗi ranh giới câu. Fixed-size cho phép kiểm soát kích thước embedding, tránh OOM và đảm bảo latency P99 < 50ms.

**Tradeoff:** Có thể cắt giữa ngữ cảnh quan trọng (ví dụ: cắt giữa câu hỏi và câu trả lời). Semantic chunking cho chất lượng tốt hơn nhưng chậm hơn ~3×.

**Phương án bị loại:** Sentence-level chunking — bị loại vì Vietnamese sentence boundary detection với underthesea không đủ chính xác với văn bản kỹ thuật.

---

### 3.2 Feature Schema — Flat vs Nested Schema

**Quyết định:** Dùng **flat schema** với tất cả feature là scalar (Int64, Float64, String).

**Lý do:** Feast SQLite online store không hỗ trợ nested types hay arrays. Flat schema đảm bảo `get_online_features()` có P99 < 5ms, dễ join với entity_rows.

**Tradeoff:** Phải pre-aggregate tất cả window features (1h, 24h, 7d) thành các cột riêng biệt thay vì lưu raw timeseries. Mất linh hoạt khi muốn thêm window mới.

---

### 3.3 Freshness Strategy — Batch vs Streaming

**Quyết định:** Dùng **batch materialization hàng giờ** cho user features (TTL=1h), **on-demand computation** cho transaction features (amount_vs_avg).

**Lý do:** User profile thay đổi chậm — refresh hàng giờ là đủ. Transaction amount chỉ biết lúc request đến — bắt buộc dùng ODFV. Chiến lược này tiết kiệm hạ tầng (không cần Kafka) nhưng vẫn đáp ứng được yêu cầu freshness cho hầu hết use case.

**Tradeoff:** Với fraud detection real-time, độ trễ 1h có thể quá lớn — cần chuyển sang stream processing (Flink + Redis). Đây là điểm hy sinh có chủ đích cho phiên bản MVP.

---

## 4. Yếu tố đặc thù Việt Nam

**Code-switching & Tokenization:** Văn bản tiếng Việt kỹ thuật thường xen tiếng Anh: *"vector embedding của câu query"*, *"feature store với TTL 1h"*. Mô hình `paraphrase-multilingual-MiniLM-L12-v2` xử lý tốt hơn các mô hình monolingual vì được huấn luyện trên 50+ ngôn ngữ. BM25 với `jieba`/`pyvi` tokenizer không nhận dạng đúng các từ chuyên ngành IT — cần custom stopword list tiếng Việt kỹ thuật.

**Quy định bảo mật:** Theo Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân, query logs chứa tên người dùng phải được mã hóa hoặc ẩn danh hóa. Multi-tenant namespacing trong semantic cache là bắt buộc, không phải tùy chọn.

---

## 5. Kết luận

Kiến trúc HybridMemoryAgent đạt được balance giữa **latency thấp** (P99 < 50ms end-to-end), **recall cao** (hybrid RRF > pure vector/BM25), và **correctness theo thời gian** (PIT join, ODFV). Phù hợp để scale lên production với chi phí hạ tầng thấp trong bối cảnh Việt Nam.
