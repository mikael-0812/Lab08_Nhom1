# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Phạm Hải Đăng  
**Vai trò:** Embed Owner  
**Ngày nộp:** 15/04/2026  
**Độ dài:** ~550 từ

---

## 1. Tôi phụ trách phần nào? (80–120 từ)

Trong bài Lab Day 10, tôi đảm nhận vai trò **Embed Owner**, chịu trách nhiệm chính về tầng lưu trữ vector (Vector Storage Layer). Các nhiệm vụ cụ thể bao gồm:

- **Module nạp dữ liệu:** Phụ trách hàm `cmd_embed_internal` trong file `etl_pipeline.py`. Tôi phải đảm bảo dữ liệu "sạch" từ Ingestion/Cleaning Owner được chuyển đổi thành vector và lưu trữ vào ChromaDB một cách tối ưu.
- **Đánh giá Retrieval:** Phụ trách file `eval_retrieval.py` để thực hiện các bài kiểm tra truy xuất tự động, nhằm cung cấp bằng chứng định lượng về hiệu quả của pipeline làm sạch dữ liệu.
- **Kết nối:** Tôi làm việc chặt chẽ với Cleaning Owner để thống nhất về cấu trúc `chunk_id` (hash-based) nhằm đảm bảo tính nhất quán giữa dữ liệu CSV và dữ liệu trong Vector DB.

---

## 2. Một quyết định kỹ thuật (100–150 từ)

Tôi đã quyết định triển khai chiến lược **Idempotency (Tính giao hoán)** kết hợp với **Pruning (Cắt tỉa)** dữ liệu cũ. Thay vì chỉ đơn giản là "delete all rồi insert", tôi sử dụng cơ chế `col.upsert` dựa trên `chunk_id` ổn định được tính toán từ nội dung và metadata của chunk.

Quyết định này mang lại hai lợi ích quan trọng:
1. **Tiết kiệm tài nguyên:** Nếu dữ liệu không thay đổi, hệ thống sẽ không cần tính toán lại embedding, giúp pipeline chạy nhanh hơn khi rerun.
2. **Snapshot Integrity:** Tôi bổ sung logic xóa các ID không còn tồn tại trong run hiện tại (`embed_prune_removed`). Điều này cực kỳ quan trọng vì nếu không có bước này, các vector lỗi (ví dụ từ version cũ hoặc từ run có inject lỗi) sẽ vẫn tồn tại trong database, dẫn đến việc Agent có thể truy xuất nhầm thông tin sai lệch dù dữ liệu mới nhất đã chuẩn.

---

## 3. Một lỗi hoặc anomaly đã xử lý (100–150 từ)

Trong Sprint 3, khi thực hiện kịch bản "Inject Corruption" (chạy pipeline mà không có rule fix refund), tôi phát hiện một anomaly thú vị liên quan đến việc cập nhật chỉ mục. 

**Triệu chứng:** Sau khi chạy lại pipeline chuẩn sau bản inject, tôi thấy log ghi nhận `embed_prune_removed=1`. 
**Nguyên nhân:** Khi rule fix refund (14 ngày -> 7 ngày) được bật/tắt, nội dung văn bản thay đổi, dẫn đến mã hash của `chunk_id` thay đổi hoàn toàn. Hệ thống nhận diện đây là một record hoàn toàn mới.
**Xử lý:** Nhờ cơ chế Pruning tôi đã cài đặt, ID cũ (chứa thông tin 14 ngày) đã bị phát hiện là "lạc lạc" và bị xóa khỏi collection ngay lập tức. Nếu không xử lý bước này, collection sẽ chứa cả 2 phiên bản "7 ngày" và "14 ngày", khiến kết quả đánh giá retrieval bị nhiễu và Agent có rủi ro trích dẫn cả thông tin cũ. Bằng chứng log `embed_prune_removed=1` trong run `inject-bad` là minh chứng rõ nhất cho việc hệ thống đã tự "dọn dẹp" thành công.

---

## 4. Bằng chứng trước / sau (80–120 từ)

Tôi đã thực hiện so sánh kết quả truy xuất cho câu hỏi về chính sách hoàn tiền (`q_refund_window`) giữa hai phiên chạy:

- **Trước (Run: `inject-bad`):** 
  `q_refund_window | top1_doc_id=policy_refund_v4 | contains_expected=yes | hits_forbidden=YES`
  Log này cho thấy dù tìm được chunk đúng, nhưng trong top-k kết quả vẫn dính thông tin "14 ngày làm việc" (bị cấm).
  
- **Sau (Run: `2026-04-15T09-24Z`):** 
  `q_refund_window | top1_doc_id=policy_refund_v4 | contains_expected=yes | hits_forbidden=no`
  Sau khi pipeline fix dữ liệu và tôi thực hiện prune vector cũ, kết quả hoàn toàn sạch, không còn residue của thông tin sai lệch.

---

## 5. Cải tiến tiếp theo (40–80 từ)

Nếu có thêm 2 giờ, tôi sẽ nâng cấp hệ thống đánh giá bằng cách tích hợp **LLM-judge**. Thay vì chỉ so khớp keyword (cứ thấy "14 ngày" là báo FAIL), tôi muốn LLM đánh giá xem thông tin đó có bị Agent hiểu nhầm là chính sách hiện hành hay không. Ngoài ra, tôi muốn triển khai **Vector Versioning** để có thể rollback vector store về các run_id trước đó một cách tức thời nếu phát hiện sự cố chất lượng ở tầng publish.
