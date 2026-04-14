# Routing Decisions Log — Lab Day 09

**Nhóm:** ___________  
**Ngày:** ___________

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
**MCP tools được gọi:** None  
**Workers called sequence:** supervisor -> retrieval_worker -> synthesis_worker

**Kết quả thực tế:**
- final_answer (ngắn): SLA xử lý ticket P1 là phản hồi 15p, xử lý 4h...
- confidence: 0.46
- Correct routing? Yes

**Nhận xét:** 
Routing này đúng vì đây là câu hỏi tra cứu thông tin SLA thông thường, không chứa từ khóa nhạy cảm về chính sách cấp quyền hay rủi ro cao cần xử lý đặc biệt.

---

## Routing Decision #2

**Task đầu vào:**
> Ai phải phê duyệt để cấp quyền Level 3?

**Worker được chọn:** `policy_tool_worker`  
**Route reason (từ trace):** `task contains policy/access keyword`  
**MCP tools được gọi:** search_kb  
**Workers called sequence:** supervisor -> policy_tool_worker -> synthesis_worker

**Kết quả thực tế:**
- final_answer (ngắn): Cần phê duyệt từ Line Manager, IT Admin và IT Security.
- confidence: 0.45
- Correct routing? Yes

**Nhận xét:**
Routing đúng vì từ khóa "cấp quyền" (access) kích hoạt policy_tool_worker để kiểm tra các quy định bảo mật và ma trận phê duyệt. Worker này đã gọi MCP `search_kb` để lấy tài liệu.

---

## Routing Decision #3

**Task đầu vào:**
> Sản phẩm kỹ thuật số (license key) có được hoàn tiền không?

**Worker được chọn:** `policy_tool_worker`  
**Route reason (từ trace):** `task contains policy/access keyword`  
**MCP tools được gọi:** search_kb  
**Workers called sequence:** supervisor -> policy_tool_worker -> synthesis_worker

**Kết quả thực tế:**
- final_answer (ngắn): Không được hoàn tiền theo quy định về hàng kỹ thuật số.
- confidence: 0.44
- Correct routing? Yes

**Nhận xét:**
Routing đúng vì câu hỏi liên quan đến chính sách hoàn tiền có điều kiện ngoại lệ. Policy_tool_worker đã phát hiện ra `digital_product_exception` thông qua logic phân tích chính sách.

---

## Routing Decision #4 (tuỳ chọn — bonus)

**Task đầu vào:**
> _________________

**Worker được chọn:** `___________________`  
**Route reason:** `___________________`

**Nhận xét: Đây là trường hợp routing khó nhất trong lab. Tại sao?**

_________________

---

## Tổng kết

### Routing Distribution

| Worker | Số câu được route | % tổng |
|--------|------------------|--------|
| retrieval_worker | ___ | ___% |
| policy_tool_worker | ___ | ___% |
| human_review | ___ | ___% |

### Routing Accuracy

> Trong số X câu nhóm đã chạy, bao nhiêu câu supervisor route đúng?

- Câu route đúng: ___ / ___
- Câu route sai (đã sửa bằng cách nào?): ___
- Câu trigger HITL: ___

### Lesson Learned về Routing

> Quyết định kỹ thuật quan trọng nhất nhóm đưa ra về routing logic là gì?  
> (VD: dùng keyword matching vs LLM classifier, threshold confidence cho HITL, v.v.)

1. ___________________
2. ___________________

### Route Reason Quality

> Nhìn lại các `route_reason` trong trace — chúng có đủ thông tin để debug không?  
> Nếu chưa, nhóm sẽ cải tiến format route_reason thế nào?

_________________
