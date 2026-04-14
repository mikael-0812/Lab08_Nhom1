# Routing Decisions Log — Lab Day 09

**Nhóm:** [Điền tên nhóm]  
**Ngày:** [Điền ngày nộp]

> **Hướng dẫn:** Ghi lại ít nhất **3 quyết định routing** thực tế từ trace của nhóm.
> Không ghi giả định — phải từ trace thật (`artifacts/traces/`).
> 
> Mỗi entry phải có: task đầu vào → worker được chọn → route_reason → kết quả thực tế.

---

## Routing Decision #1

**Task đầu vào:**
> SLA xử lý ticket P1 là bao lâu?

**Worker được chọn:** `retrieval_worker`  
**Route reason (từ trace):** `default route`  
**MCP tools được gọi:** Không có  
**Workers called sequence:** `retrieval_worker -> synthesis_worker`

**Kết quả thực tế:**
- final_answer (ngắn): Hệ thống tổng hợp câu trả lời từ evidence retrieval về SLA P1.
- confidence: `0.10`
- Correct routing? Yes

**Nhận xét:**  
Đây là một routing hợp lý vì câu hỏi mang tính tra cứu tri thức trực tiếp từ tài liệu SLA, không cần policy check hay external tool. Supervisor route sang `retrieval_worker` là phù hợp với loại câu hỏi single-document, và không làm tăng thêm chi phí không cần thiết.

---

## Routing Decision #2

**Task đầu vào:**
> Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?

**Worker được chọn:** `policy_tool_worker`  
**Route reason (từ trace):** `task contains policy/access keyword`  
**MCP tools được gọi:** Có  
**Workers called sequence:** `policy_tool_worker -> retrieval_worker -> synthesis_worker`

**Kết quả thực tế:**
- final_answer (ngắn): Hệ thống xử lý qua policy path rồi mới tổng hợp câu trả lời từ retrieval.
- confidence: `0.10`
- Correct routing? Yes

**Nhận xét:**  
Routing này hợp lý vì câu hỏi thuộc nhóm policy/refund. Việc supervisor chọn `policy_tool_worker` trước cho phép pipeline ưu tiên nhánh xử lý phù hợp với chính sách, sau đó mới kết hợp retrieval để lấy bằng chứng. Đây là ví dụ rõ nhất cho lợi ích của supervisor-worker so với single-agent.

---

## Routing Decision #3

**Task đầu vào:**
> ERR-403-AUTH là lỗi gì và cách xử lý?

**Worker được chọn:** `human_review`  
**Route reason (từ trace):** `unknown error code + risk_high → human review`  
**MCP tools được gọi:** Không có  
**Workers called sequence:** `human_review -> retrieval_worker -> synthesis_worker`

**Kết quả thực tế:**
- final_answer (ngắn): Hệ thống không có đủ dữ liệu rõ ràng, nên đi qua nhánh human review trước khi tiếp tục retrieval.
- confidence: `0.10`
- Correct routing? Yes

**Nhận xét:**  
Đây là quyết định routing quan trọng nhất trong trace vì nó thể hiện rõ vai trò của `risk_high` và HITL. Với mã lỗi không rõ trong docs, việc route thẳng sang retrieval có thể dẫn đến hallucination hoặc câu trả lời thiếu kiểm soát. Human-review placeholder ở đây giúp pipeline thận trọng hơn.

---

## Routing Decision #4 (tuỳ chọn — bonus)

**Task đầu vào:**
> Ticket P1 lúc 2am. Cần cấp Level 2 access tạm thời cho contractor đang on-call.

**Worker được chọn:** `policy_tool_worker`  
**Route reason:** `task contains policy/access keyword`

**Nhận xét: Đây là trường hợp routing khó nhất trong lab. Tại sao?**  
Đây là trường hợp khó vì câu hỏi chứa đồng thời nhiều tín hiệu: SLA/P1, access level, contractor và bối cảnh khẩn cấp ngoài giờ. Nó có thể cần cả retrieval lẫn policy reasoning. Tuy nhiên, supervisor hiện tại ưu tiên keyword-based routing, nên route sang `policy_tool_worker` trước. Điều này hợp lý ở mức heuristic, nhưng cũng cho thấy nếu muốn xử lý tốt hơn các câu multi-hop, routing logic cần giàu ngữ nghĩa hơn.

---

## Tổng kết

### Routing Distribution

| Worker | Số câu được route | % tổng |
|--------|------------------|--------|
| retrieval_worker | 8 | 53% |
| policy_tool_worker | 7 | 46% |
| human_review | 1 | 6% |

### Routing Accuracy

> Trong số 15 câu nhóm đã chạy, bao nhiêu câu supervisor route đúng?

- Câu route đúng: 15 / 15 ở mức routing heuristic hiện tại
- Câu route sai (đã sửa bằng cách nào?): 0 câu được xác nhận là route sai từ trace đã chạy
- Câu trigger HITL: 1

### Lesson Learned về Routing

> Quyết định kỹ thuật quan trọng nhất nhóm đưa ra về routing logic là gì?

1. Ưu tiên keyword-based routing đơn giản để hệ thống chạy ổn định trước khi tăng độ phức tạp.
2. Tách riêng nhánh `human_review` cho các trường hợp rủi ro cao như mã lỗi không rõ để giảm nguy cơ hallucination.

### Route Reason Quality

> Nhìn lại các `route_reason` trong trace — chúng có đủ thông tin để debug không?  
> Nếu chưa, nhóm sẽ cải tiến format route_reason thế nào?

`route_reason` hiện tại đủ để hiểu logic route ở mức cơ bản, ví dụ biết câu nào đi qua policy branch hoặc human review. Tuy nhiên, để debug tốt hơn trong các case multi-hop, nên mở rộng format route_reason theo hướng có cấu trúc hơn, chẳng hạn:
- `matched_keywords=[refund, level 3]`
- `risk_flags=[unknown_error_code]`
- `override=human_review`

Cách này sẽ giúp trace vừa dễ đọc vừa dễ phân tích tự động hơn trong Sprint 4.
