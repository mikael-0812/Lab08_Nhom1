# Báo cáo Cá nhân - Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Đào Quang Thắng  
**Vai trò:** Worker Owner  
**Module phụ trách:** `retrieval.py`, `policy_tool.py`, `synthesis.py`, `contracts/`

---

## 1. Phần việc phụ trách thực tế
Trong dự án này, tôi chịu trách nhiệm xây dựng "hệ thống cơ bắp và trí tuệ" cho Agent thông qua việc triển khai 3 worker chuyên biệt và hệ thống hợp đồng dữ liệu:
*   **Retrieval Worker**: Kết nối với ChromaDB, thực hiện tìm kiếm ngữ nghĩa (Dense Search) để lấy ra các đoạn văn bản liên quan nhất.
*   **Policy Tool Worker**: Đây là phần quan trọng nhất, tôi đã cài đặt logic để phát hiện các ngoại lệ về chính sách (như Flash Sale, hàng kỹ thuật số) và tích hợp các công cụ MCP để tra cứu thông tin thời gian thực.
*   **Synthesis Worker**: Xây dựng Prompt grounded để tổng hợp câu trả lời cuối cùng, đảm bảo mọi thông tin đều có trích dẫn nguồn [tên_file] và tính toán điểm tin cậy (confidence score) thực tế.
*   **Worker Contracts**: Thiết kế file YAML định nghĩa chặt chẽ đầu vào/đầu ra để Supervisor và các Worker có thể phối hợp nhịp nhàng.

## 2. Một quyết định kỹ thuật quan trọng
**Quyết định**: *Thực hiện kiểm tra chính sách (Policy Check) chuyên biệt trước khi tổng hợp câu trả lời.*

**Bối cảnh**: Trong các hệ thống RAG thông thường (như Day 08), LLM thường nhận một lượng lớn context và tự quyết định câu trả lời. Điều này dễ dẫn đến việc bỏ sót các điều khoản loại trừ nhỏ nhưng quan trọng (ví dụ: hàng Flash Sale không được hoàn tiền dù sản phẩm có lỗi).

**Lý do chọn**: Việc tách riêng một `policy_tool_worker` giúp hệ thống có một bước "kiểm tra cứng" về logic chính sách. Tôi sử dụng kết hợp giữa Keyword Matching (độ chính xác cao, nhanh) và LLM Analysis để quét qua các ngoại lệ trước khi gửi dữ liệu cho Synthesis Worker. Điều này đảm bảo tính tuân thủ chính sách gần như tuyệt đối cho hệ thống Helpdesk.

## 3. Một lỗi (bug) đã gặp và cách xử lý
**Lỗi**: `UnicodeEncodeError: 'charmap' codec can't encode characters...`

**Mô tả**: Khi chạy hệ thống trên terminal Windows, các câu trả lời có tiếng Việt hoặc các ký tự đặc biệt trong tên file tài nguyên làm cho script bị crash ngay khi in kết quả ra màn hình.

**Cách xử lý**: 
1. Tôi đã chỉnh sửa hàm `open()` trong các script `eval_trace.py` và các workers để luôn sử dụng `encoding="utf-8"`.
2. Thiết lập biến môi trường `PYTHONIOENCODING="utf-8"` trong quá trình thực thi để đảm bảo luồng I/O của Python hiểu được các ký tự UTF-8 trên Windows. Điều này giúp hệ thống hiển thị tiếng Việt mượt mà và không còn bị lỗi crash khi xử lý trace JSON.

## 4. Tự đánh giá
*   **Điểm mạnh**: Đã triển khai được cơ chế tính `confidence` score thực tế dựa trên độ tương đồng của văn bản và các ngoại lệ chính sách, thay vì dùng một con số cố định. Điều này giúp hệ thống có khả năng tự nhận biết khi nào câu trả lời không chắc chắn.
*   **Điểm yếu**: Logic Routing trong Supervisor vẫn còn phụ thuộc nhiều vào quy tắc (rules), nếu có thời gian tôi sẽ nâng cấp Worker của mình để có thể tự học hoặc điều chỉnh tham số tìm kiếm động.
*   **Sự đóng góp**: Tôi đóng vai trò là người xây dựng nền tảng dữ liệu cho nhóm, giúp Supervisor có đủ "nguyên liệu" chuẩn để phục vụ người dùng.

## 5. Nếu có thêm 2 giờ làm việc
Tôi sẽ triển khai thêm bước **Cross-Encoder Reranking**. Hiện tại chúng ta mới dùng Bi-Encoder (cosine similarity) để lấy dữ liệu, khâu Reranking sẽ giúp đánh giá lại độ liên quan của từng chunk văn bản với câu hỏi một cách sâu sắc hơn, từ đó loại bỏ được các nội dung nhiễu và tăng độ chính xác của khâu Synthesis lên mức cao nhất.
