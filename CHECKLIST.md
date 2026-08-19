# 📋 CHECKLIST CÁC CÔNG VIỆC CẦN LÀM - LAB 19 (TRACK 2)
> **Dự án:** Vector Store + Feature Store Lab  
> **Tổng quan điểm số:** 100 điểm Core (NB1–NB4) + 50 điểm Advanced (NB5–NB8) + 20 điểm Bonus Optional.

---

## 1. 🚀 Khởi tạo & Môi trường (Setup)

- [x] **Chạy script khởi tạo môi trường (Lite Path / Docker Path):**
  - [x] Sửa lỗi kích hoạt venv trên Windows cho `setup-lite.sh` và `setup-docker.sh`. *(Đã hoàn thành)*
  - [x] Khởi chạy setup: `bash setup-lite.sh` *(Đã hoàn thành - All checks passed)*
- [x] **Sinh dữ liệu mẫu:**
  - [x] Đã tạo `data/corpus_vn.jsonl` (1000 docs) và `data/golden_set.jsonl` (50 queries), `agent_queries.jsonl` & `user_spend.parquet`. *(Đã hoàn thành)*
- [x] **Chuyển đổi notebook Jupytext sang `.ipynb`:**
  - [x] Đã sinh đầy đủ 8 file `.ipynb` (`01_embeddings_index.ipynb` đến `08_feature_engineering.ipynb`). *(Đã hoàn thành)*
- [x] **Đọc tài liệu định hướng:**
  - [x] Đọc file [`VIBE-CODING.md`](VIBE-CODING.md) (5–10 phút) để nắm vững workflow TDD/SDD và kinh nghiệm phối hợp với AI Assistant. *(Đã hoàn thành)*

---

## 2. 🎯 Khối Bắt Buộc — Core Lab (100 điểm)

### 📌 Notebook 01: Embeddings & Vector Indexing (`01_embeddings_index`) — 20 pts
- [x] **Thực thi cell #4 (TODO):** Cài đặt vòng lặp embed 1000 văn bản corpus bằng `fastembed` và upsert vào Qdrant collection `lab19`. *(Đã hoàn thành)*
- [x] **Kiểm tra chỉ số:** Đảm bảo `client.count("lab19").count == 1000` *(5 pts)*. *(Đã hoàn thành)*
- [x] **Truy vấn từ khóa:** Thực hiện search keyword query (cell §5) và hiển thị Top-5 kết quả trả về *(5 pts)*. *(Đã hoàn thành)*
- [x] **Truy vấn diễn đạt lại (Paraphrase query):** Chạy câu query tiếng Việt diễn đạt lại (không chứa từ khóa gốc), kiểm tra Top-5 kết quả thuộc về đúng chủ đề (`cloud`) *(10 pts)*. *(Đã hoàn thành)*
- [X] **Lưu ảnh chụp màn hình:** Chụp lại output của NB1 và lưu vào `submission/screenshots/nb1_indexing.png`. *(Học viên chỉ cần mở notebook trong Jupyter và chụp màn hình)*

---

### 📌 Notebook 02: Hybrid Search & RRF (`02_hybrid_search_rrf`) — 25 pts
- [x] **Cài đặt hàm `search_hybrid` (TODO):** Triển khai công thức Reciprocal Rank Fusion: $score(d) = \sum \frac{1}{k + rank(d)}$, với $k=60$ và rank tính từ 1 (1-based) *(10 pts)*. *(Đã hoàn thành)*
- [x] **Đánh giá Precision@10 tổng thể:** Chạy benchmark trên 50 golden queries. Bảng kết quả thỏa mãn: Hybrid (78.6%) > Keyword (77.8%) VÀ Hybrid (78.6%) > Semantic (73.2%) *(10 pts)*. *(Đã hoàn thành)*
- [x] **Phân tích theo Slice:** Xuất bảng Precision@10 phân loại theo câu hỏi (`mixed`: 100.0% Hybrid thắng, `exact`: 96.7%, `paraphrase`: 32.0%) *(5 pts)*. *(Đã hoàn thành)*
- [x] **Lưu ảnh chụp màn hình:** Chụp lại bảng Precision@10 và lưu vào `submission/screenshots/nb2_hybrid.png`. *(Đã hoàn thành)*

---

### 📌 Notebook 03: Search API & Latency Benchmark (`03_search_api_benchmark`) — 25 pts
- [x] **Hoàn thiện API Endpoint:** Cài đặt route `GET /search` trong [`app/main.py`](app/main.py) trả về `SearchResponse` hợp lệ có chứa field `latency_ms` *(5 pts)*. *(Đã hoàn thành)*
- [x] **Chạy Latency Benchmark (TODO):** Thực hiện đo 100 queries x 3 modes (`kw`, `sem`, `hybrid`) server-side và in ra bảng latency P50 / P95 / P99 *(10 pts)*. *(Đã hoàn thành)*
- [x] **Đạt chỉ tiêu P99:** Đảm bảo mode `hybrid` đạt server-side P99 < 50ms sau khi đã chạy warmup queries *(10 pts)*. *(Đã hoàn thành)*
- [x] **Lưu ảnh chụp màn hình:** Chụp lại mẫu response `/search` và bảng latency P50/P95/P99 lưu vào `submission/screenshots/nb3_api_benchmark.png`. *(Đã hoàn thành)*

---

### 📌 Notebook 04: Feast Feature Store (`04_feast_feature_store`) — 25 pts
- [x] **Đăng ký Feature Views:** Đăng ký 3 feature views trong Feast (`app/feast_repo/feature_views.py`), chạy `feast apply` thành công và hiển thị 3 views khi gõ `feast feature-views list` *(5 pts)*. *(Đã hoàn thành)*
- [x] **Materialize dữ liệu:** Chạy `materialize-incremental` đẩy dữ liệu vào Online Store (SQLite / Redis) mà không báo lỗi *(5 pts)*. *(Đã hoàn thành)*
- [x] **Online Lookup:** Chạy `get_online_features()` cho entity `user_id="u_001"` và nhận được kết quả dict hợp lệ *(5 pts)*. *(Đã hoàn thành)*
- [x] **Đo độ trễ Online Lookup (TODO):** Thực hiện 100 lần lookup và báo cáo độ trễ P99 (khuyên dùng P99 < 10ms) *(5 pts)*. *(Đã hoàn thành)*
- [x] **Point-In-Time (PIT) Join:** Thực thi `get_historical_features()` trả về DataFrame chuẩn 3 dòng x N features không bị rò rỉ dữ liệu (target leakage) *(5 pts)*. *(Đã hoàn thành)*
- [X] **Lưu ảnh chụp màn hình:** Chụp lại kết quả PIT join (DataFrame 3 dòng) và kết quả online lookup lưu vào `submission/screenshots/nb4_feast.png`.

---

## 3. 🔬 Khối Nâng Cao — Advanced Missions (50 điểm)

- [x] **Tạo dữ liệu cho khối nâng cao:** Chạy `python scripts/gen_agent_queries.py` và `python scripts/gen_spend.py` (hoặc `make gen-advanced`). *(Đã hoàn thành)*

### 📌 Notebook 05: Filtered Search (`05_filtered_search`) — 10 pts
- [x] **Recall Cliff Table:** Tạo bảng so sánh recall theo độ chọn lọc: Chứng minh `post-filter` sập mạnh khi filter bị siết chặt (~4%), trong khi `filtered-ANN` duy trì recall = 1.00 *(5 pts)*. *(Đã hoàn thành)*
- [x] **Over-fetch Ladder:** Xây dựng ladder over-fetch chứng minh `fetch_k` phải lấy tới ~50% corpus mới cứu được recall của post-filter *(5 pts)*. *(Đã hoàn thành)*

### 📌 Notebook 06: Agentic Retrieval (`06_agent_retrieval`) — 12 pts
- [x] **Đo hiệu năng Agentic vs Single-shot:** Lập bảng so sánh 3 chiến lược với **cùng ngân sách 16 docs**: Chứng minh Agentic vượt trội Single-shot về cả `recall` lẫn `balance` *(5 pts)*. *(Đã hoàn thành)*
- [x] **Giải thích Reflection:** Giải thích ngắn gọn lý do tại sao `agentic (+filter)` lại cho kết quả thấp hơn `agentic (no filter)` *(4 pts)*. *(Đã hoàn thành)*
- [x] **Hàm `build_context()`:** Hoàn thiện hàm ghép ngữ cảnh, in ra kết quả chứa đồng thời Feature (Feast) và `doc_ids` (Qdrant) *(3 pts)*. *(Đã hoàn thành)*

### 📌 Notebook 07: Semantic Cache & Multi-Tenant Security (`07_semantic_cache`) — 12 pts
- [x] **Bảng Sweep Ngưỡng (Threshold Sweep):** Báo cáo bảng có đủ 2 cột: tỷ lệ tiết kiệm (%) và số câu trả lời sai *(5 pts)*. *(Đã hoàn thành)*
- [x] **Lựa chọn Ngưỡng & Giải thích:** Chọn ngưỡng cosine similarity hợp lý cho corpus và giải thích lý do tại sao 0.75 chưa đủ an toàn *(4 pts)*. *(Đã hoàn thành)*
- [x] **Demo Rò rỉ Chéo Tenant (Multi-Tenant Leak):** Demo chứng minh bị rò rỉ dữ liệu khi `namespaced=False` (LEAK) và bảo mật thành công khi `namespaced=True` (MISS) *(3 pts)*. *(Đã hoàn thành)*

### 📌 Notebook 08: Feature Engineering & Leakage (`08_feature_engineering`) — 12 pts
- [x] **Bảng Leakage Target Encoding:** Chứng minh `target-naive` bị chênh lệch gap > 0.30 trên `session_id`, còn in-fold $\approx 0$ *(4 pts)*. *(Gap = 0.477 ✅)*
- [x] **PIT vs Latest Join:** Đo đạc và báo cáo % dòng bị rò rỉ cùng sự chênh lệch AUC khi join sai thời điểm *(4 pts)*. *(98.2% dòng rò, AUC diff = +0.120 ✅)*
- [x] **On-Demand Feature View (ODFV):** Khởi tạo ODFV trả về 2 giá trị `amount_vs_avg` khác nhau cho cùng một user khi đầu vào `amount` thay đổi *(4 pts)*. *(ratio 0.03 vs 4.21 ✅)*

- [x] **Kiểm tra tự động toàn bộ project:** Chạy `make test` và `make verify-lite` (hoặc `make verify-docker`) đảm bảo 100% xanh *(4 pts)*. *(41/41 tests PASSED ✅)*

---

## 4. 📝 Nộp Bài & Minh Chứng (Submission)

- [x] **Giữ nguyên cell output trong Jupyter Notebooks:** Đảm bảo tất cả 4 (hoặc 8) file `.ipynb` đều đã được run và giữ nguyên kết quả các cell. *(Đã hoàn thành — NB01–NB08 có output ✅)*
- [x] **Kiểm tra thư mục ảnh chụp (`submission/screenshots/`):**
  - [x] `nb1_indexing.png`
  - [x] `nb2_hybrid.png`
  - [x] `nb3_api_benchmark.png`
  - [x] `nb4_feast.png`
  - [x] *(Option)* Ảnh minh chứng cho NB5 – NB8 nếu làm khối nâng cao. *(nb5_filtered_search.png ✅)*
- [x] **Điền file `submission/REFLECTION.md`:**
  - [x] Điền Tên và Cohort. *(Nguyễn Văn Hưng, A20-K3 ✅)*
  - [x] Trả lời câu hỏi (≤ 200 chữ): *Mode nào thắng ở loại query nào (`exact`/`paraphrase`/`mixed`) và tại sao? Khi nào không nên dùng hybrid?* *(Đã trả lời bằng tiếng Việt ✅)*
  - [x] Đánh dấu tick nếu có làm Bonus. *(Đã tick [x] ✅)*
- [ ] **Push code lên GitHub Public Repository:**
  - [ ] Khởi tạo / commit code:
    ```bash
    git add -A
    git commit -m "Lab 19 submission - Nguyễn Văn Hưng"
    git push -u origin main
    ```
  - [ ] **QUAN TRỌNG:** Đảm bảo Repository ở chế độ **PUBLIC** (Repo PRIVATE = 0 điểm).
- [ ] **Nộp link:** Copy URL GitHub repo public và paste vào ô submission bài tập Day 19 trên **VinUni LMS**.

---

## 5. 🎨 Bonus Challenge — Build Your Own AI Memory (Tùy chọn - 20 pts Bonus)

- [x] **Tạo thư mục `bonus/` trong repo:** *(Đã tạo ✅)*
- [x] **Viết `bonus/ARCHITECTURE.md` (≥ 600 từ):**
  - [x] Có sơ đồ kiến trúc (Mermaid / ASCII / Ảnh vẽ). *(ASCII diagram ✅)*
  - [x] Nêu 3 quyết định kiến trúc kèm **tradeoff rõ ràng** (Chủ đề Chunking, Feature Schema, Freshness Strategy). *(Đã nêu ✅)*
  - [x] Đề cập ít nhất 1 yếu tố đặc thù cho bối cảnh Việt Nam (Tokenization, Code-switching, quy định bảo mật...). *(Code-switching + Nghị định 13/2023 ✅)*
  - [x] Nêu rõ 1 phương án bị loại bỏ kèm lý do cụ thể. *(Sentence-level chunking bị loại ✅)*
- [x] **Cài đặt `bonus/agent.py`:** Triển khai class `HybridMemoryAgent` có 2 phương thức `.remember()` và `.recall()`. *(Đã cài đặt ✅)*
- [x] **Chạy `bonus/demo.py`:** Script minh họa 5 loại câu hỏi khác nhau, chạy thành công (exit code 0) và in ra assembled context. *(5/5 queries PASSED, in-memory Qdrant ✅)*
