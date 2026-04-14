# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Phạm Hoàng Kim Liên
**Vai trò trong nhóm:** MCP Owner 
**Ngày nộp:** 14/04/2026  
**Độ bài yêu cầu:** 500–800 từ (Bản cập nhật sau khi tối ưu Retrieval)

---

## 1. Tôi phụ trách phần nào? (100–150 từ)

Trong dự án Lab Day 09, bên cạnh trách nhiệm chính về module **MCP (Model Context Protocol) Server**, tôi đã đảm nhận thêm phần tối ưu hóa và sửa lỗi cho pipeline **Retrieval & Indexing**. Cụ thể:
- **File chính:** `mcp_server.py`, `mcp_interactive.py`, `workers/retrieval.py` và `reindex_data.py` (mới).
- **Functions tôi implement/tối ưu:** Xây dựng bộ công cụ MCP (`search_kb`, `get_ticket_info`), sửa lỗi mã hóa (Encoding) trong worker retrieval, và thiết kế lại quy trình Indexing dữ liệu vào ChromaDB bằng script `reindex_data.py`.

**Cách công việc của tôi kết nối với phần của thành viên khác:**
Phần việc của tôi cung cấp "dữ liệu sạch" cho toàn bộ hệ thống. Nếu MCP và Retrieval không hoạt động chính xác, Synthesis Worker sẽ không có đủ thông tin để trả lời (dẫn đến lỗi "Không đủ thông tin"). Tôi trực tiếp hỗ trợ Worker Owner sửa lỗi logic tìm kiếm để đảm bảo kết quả chấm điểm (grading run) đạt độ tự tin cao nhất.

**Bằng chứng:**
- File `reindex_data.py` thực hiện chia nhỏ file (chunking) thành 63 đoạn thay vì 5 đoạn như ban đầu.
- File `workers/retrieval.py` đã được xử lý lỗi Encoding (SyntaxError) giúp import ổn định.
- Kết quả trong `artifacts/grading_run.jsonl` sau khi tôi tối ưu đã có câu trả lời chi tiết cho các câu gq08, gq10 thay vì báo lỗi thiếu thông tin.

---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)

**Quyết định:** Sử dụng **Paragraph-based Chunking (phân đoạn theo đoạn văn)** thay vì index nguyên khối toàn bộ file văn bản.

**Lý do:**
Ban đầu, hệ thống chỉ index 5 file tài liệu tương ứng với 5 "chunks" khổng lồ trong ChromaDB. Điều này khiến thuật toán tìm kiếm vector (Cosine Similarity) bị nhiễu thông tin, không thể xác định chính xác các chi tiết nhỏ như "số ngày đổi mật khẩu" hay "người phê duyệt Level 3". 
Tôi đã quyết định viết lại script indexing, sử dụng kỹ thuật split văn bản dựa trên ký tự xuống dòng kép (`\n\n`). Quyết định này giúp chia nhỏ kiến thức thành từng câu hỏi FAQ hoặc từng điều khoản chính sách riêng biệt.

**Trade-off đã chấp nhận:**
Việc chia nhỏ chunk làm tăng số lượng bản ghi trong database (từ 5 lên 63), dẫn đến thời gian query tăng nhẹ. Tuy nhiên, đánh đổi này là hoàn toàn xứng đáng vì nó giải quyết triệt để lỗi "Abstain" (Agent từ chối trả lời vì không tìm thấy bằng chứng đủ mạnh).

**Bằng chứng từ trace/code:**
Trong file `reindex_data.py`, tôi đã implement logic:
```python
chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 50]
```
Sau khi áp dụng, độ tin cậy (`confidence`) của các câu hỏi trong `view_results.py` đạt mức trung bình 0.7, so với mức 0.1 trước khi tối ưu.

---

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

**Lỗi:** `SyntaxError: Non-UTF-8 code` trong file retrieval và lỗi logic **"Abstain Hallucination"**.

**Symptom:** 
Khi chạy pipeline chấm điểm, Agent liên tục trả lời "Không đủ thông tin trong tài liệu nội bộ" cho các câu hỏi rõ ràng có trong FAQ. Ngoài ra, script `retrieval.py` bị crash khi chạy độc lập do lỗi mã hóa ký tự ở dòng comment cuối cùng.

**Root cause:**
- Một comment chứa ký tự Latin lạ (Ð) không được định dạng chuẩn UTF-8 khiến Python interpreter bị lỗi.
- Database ChromaDB bị "đói" dữ liệu do cơ chế indexing cũ quá thô sơ, không cung cấp đủ context liên quan cho LLM.

**Cách sửa:**
- Tôi đã sử dụng lệnh `iconv` để làm sạch file `retrieval.py` và xóa bỏ các ký tự gây lỗi mã hóa.
- Thực hiện xóa collection cũ trên ChromaDB và chạy lại `reindex_data.py` với cơ chế chunking mới.

**Bằng chứng trước/sau:**
- **Trước:** Câu trả lời gq08 là "Không đủ thông tin", confidence 0.1.
- **Sau:** Câu trả lời gq08: "Nhân viên phải đổi mật khẩu sau 90 ngày. Hệ thống sẽ cảnh báo trước 7 ngày...", confidence 0.7.

---

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

**Tôi làm tốt nhất ở điểm nào?**
Tôi đã chủ động debug sâu vào hệ thống retrieval để tìm ra nguyên nhân gốc rễ của việc Agent trả lời sai, thay vì chỉ tập trung vào module MCP được giao. Việc thiết kế lại script indexing giúp cải thiện chất lượng của toàn bộ 10 câu hỏi chấm điểm.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**
Tôi mất khá nhiều thời gian ban đầu để loay hoay với lỗi Encoding của Python trên MacOS, điều này có thể đã được xử lý nhanh hơn nếu tôi nắm vững các công cụ dòng lệnh xử lý text từ đầu.

**Nhóm phụ thuộc vào tôi ở đâu?**
Nhóm phụ thuộc vào tôi để có một Knowledge Base hoạt động ổn định. Nếu không có phần tối ưu retrieval của tôi, điểm số của nhóm trong phần "Accuracy" và "Citation" sẽ rất thấp.

**Phần tôi phụ thuộc vào thành viên khác:**
Tôi phụ thuộc vào Worker Owner (SLA/Policy) để cung cấp các test case thực tế nhằm kiểm chứng xem các đoạn văn bản tôi chunk ra đã thực sự tối ưu hay chưa.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)

Tôi sẽ triển khai kỹ thuật **Semantic Chunking** thay vì chỉ split theo ký tự xuống dòng. Tôi nhận thấy ở câu gq09, Agent vẫn còn bị sót một phần nhỏ thông tin do việc split thủ công đôi khi cắt ngang các quy trình liên quan. Nếu dùng LLM hoặc thư viện như LangChain để split theo ngữ nghĩa, chất lượng truy xuất sẽ còn hoàn hảo hơn nữa.

---
*Lưu file này với tên: `reports/individual/PhamHoangKimLien.md`*  
