# Reflection — Lab 19

**Tên:** Nguyễn Văn Hưng
**Cohort:** A20-K3
**Path đã chạy:** both (lite + docker)

---

## Câu hỏi (≤ 200 chữ)

> Trên golden set 50 queries, mode nào thắng ở loại query nào (`exact` /
> `paraphrase` / `mixed`), và tại sao? Khi nào bạn **không** dùng hybrid
> (i.e. khi nào pure BM25 hoặc pure vector là lựa chọn đúng)?

Trên 50 queries của golden set:

- **`exact`**: BM25 thuần thắng (Precision@10 = 96.7%) vì query chứa từ khóa chính xác — BM25 match trực tiếp, không cần ngữ nghĩa.
- **`paraphrase`**: Vector thuần thắng vì query dùng từ ngữ khác nhau — embedding nắm bắt ngữ nghĩa tốt hơn term matching.
- **`mixed`**: Hybrid (RRF) thắng tuyệt đối (100%) vì kết hợp cả hai điểm mạnh.

**Khi không dùng hybrid:**
- Corpus nhỏ, query luôn exact → BM25 đủ, hybrid không tăng thêm.
- Toàn bộ query là paraphrase / mô tả ngữ nghĩa → pure vector cho latency thấp hơn mà recall tương đương.
- Khi tài nguyên tính toán hạn chế và P99 < 20ms là ưu tiên tuyệt đối.

---

## Điều ngạc nhiên nhất khi làm lab này

`target-naive` encoding trên `session_id` cho train AUC = 0.999 nhưng test AUC chỉ 0.522 — chênh lệch 0.477! Lỗi không nằm ở code mà ở **thứ tự thao tác**: encode trước rồi mới split là đủ để model học thuộc nhãn mà không ai hay biết.

---

## Bonus challenge

- [x] Đã làm bonus (xem `bonus/`)
- [ ] Pair work với: _(không có đồng đội)_
