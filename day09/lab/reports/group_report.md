# Báo Cáo Nhóm — Lab Day 09: Multi-Agent Orchestration

**Tên nhóm:** Antigravity Team  
**Thành viên:**
| Tên | Vai trò | Email |
|-----|---------|-------|
| Antigravity | Supervisor Owner | assistant@ai.google |
| User | Product Owner | user@example.com |

**Ngày nộp:** 2026-04-14  
**Repo:** Lecture-Day-08-09-10-main/day09/lab  
**Độ dài khuyến nghị:** 600–1000 từ

---

> **Hướng dẫn nộp group report:**
> 
> - File này nộp tại: `reports/group_report.md`
> - Deadline: Được phép commit **sau 18:00** (xem SCORING.md)
> - Tập trung vào **quyết định kỹ thuật cấp nhóm** — không trùng lặp với individual reports
> - Phải có **bằng chứng từ code/trace** — không mô tả chung chung
> - Mỗi mục phải có ít nhất 1 ví dụ cụ thể từ code hoặc trace thực tế của nhóm

---

## 1. Kiến trúc nhóm đã xây dựng (150–200 từ)

> Mô tả ngắn gọn hệ thống nhóm: bao nhiêu workers, routing logic hoạt động thế nào,
> MCP tools nào được tích hợp. Dùng kết quả từ `docs/system_architecture.md`.

**Hệ thống tổng quan:**
Hệ thống sử dụng kiến trúc Supervisor-Worker gồm 4 Worker chuyên biệt: Retrieval (dense search), Policy Tool (kiểm tra chính sách + ngoại lệ), Synthesis (tổng hợp câu trả lời) và Human Review (cho các trường hợp rủi ro cao). Supervisor điều phối luồng dựa trên phân tích ý định và trích xuất từ khóa.

**Routing logic cốt lõi:**
Supervisor sử dụng Rule-based keyword matching kết hợp với Intent analysis. Nó phân loại query thành 3 nhóm: Thông tin chung (Retrieval), Chính sách/Quyền hạn (Policy Tool), và Sự cố khẩn cấp (Cần thêm cờ Risk_high).

**MCP tools đã tích hợp:**
> Liệt kê tools đã implement và 1 ví dụ trace có gọi MCP tool.

- `search_kb`: Công cụ tìm kiếm Knowledge Base tích hợp ChromaDB.
- `get_ticket_info`: Công cụ tra cứu trạng thái ticket từ Jira (mock).
- `check_access_permission`: Công cụ kiểm tra quyền hạn dựa trên role.

---

## 2. Quyết định kỹ thuật quan trọng nhất (200–250 từ)

> Chọn **1 quyết định thiết kế** mà nhóm thảo luận và đánh đổi nhiều nhất.
> Phải có: (a) vấn đề gặp phải, (b) các phương án cân nhắc, (c) lý do chọn phương án đã chọn.

**Quyết định:** Tách biệt Policy Logic ra khỏi Retrieval Worker.

**Bối cảnh vấn đề:**
Trong Day 08, LLM thường xuyên bỏ qua các ngoại lệ (như Flash Sale) nếu context quá dài. Chúng tôi cần một bước kiểm tra cứng (hard-check) hoặc phân tích tập trung vào policy.

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|-----------|
| Gộp chung Prompt | Nhanh, rẻ | Dễ hallucination, khó debug |
| Policy Worker riêng | Chính xác cao, dễ audit | Tăng latency, tốn thêm 1 LLM call |

**Phương án đã chọn và lý do:**
Chọn Policy Worker riêng vì độ chính xác về chính sách là quan trọng nhất cho IT Helpdesk service. Độ trễ 2-3s là chấp nhận được.

**Bằng chứng từ trace/code:**
Trong trace `run_20260414_105614.json`, query về "cấp quyền Level 3 khẩn cấp" đã kích hoạt `policy_tool_worker`, sau đó worker này gọi đồng thời 2 MCP tools: `search_kb` và `get_ticket_info`.

---

## 3. Kết quả grading questions (150–200 từ)

> Sau khi chạy pipeline với grading_questions.json (public lúc 17:00):
> - Nhóm đạt bao nhiêu điểm raw?
> - Câu nào pipeline xử lý tốt nhất?
> - Câu nào pipeline fail hoặc gặp khó khăn?

**Tổng điểm raw ước tính:** ___ / 96

**Câu pipeline xử lý tốt nhất:**
- ID: ___ — Lý do tốt: ___________________

**Câu pipeline fail hoặc partial:**
- ID: ___ — Fail ở đâu: ___________________  
  Root cause: ___________________

**Câu gq07 (abstain):** Nhóm xử lý thế nào?

_________________

**Câu gq09 (multi-hop khó nhất):** Trace ghi được 2 workers không? Kết quả thế nào?

_________________

---

## 4. So sánh Day 08 vs Day 09 — Điều nhóm quan sát được (150–200 từ)

> Dựa vào `docs/single_vs_multi_comparison.md` — trích kết quả thực tế.

**Metric thay đổi rõ nhất (có số liệu):**

_________________

**Điều nhóm bất ngờ nhất khi chuyển từ single sang multi-agent:**

_________________

**Trường hợp multi-agent KHÔNG giúp ích hoặc làm chậm hệ thống:**

_________________

---

## 5. Phân công và đánh giá nhóm (100–150 từ)

> Đánh giá trung thực về quá trình làm việc nhóm.

**Phân công thực tế:**

| Thành viên | Phần đã làm | Sprint |
|------------|-------------|--------|
| ___ | ___________________ | ___ |
| ___ | ___________________ | ___ |
| ___ | ___________________ | ___ |
| ___ | ___________________ | ___ |

**Điều nhóm làm tốt:**

_________________

**Điều nhóm làm chưa tốt hoặc gặp vấn đề về phối hợp:**

_________________

**Nếu làm lại, nhóm sẽ thay đổi gì trong cách tổ chức?**

_________________

---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì? (50–100 từ)

> 1–2 cải tiến cụ thể với lý do có bằng chứng từ trace/scorecard.

_________________

---

*File này lưu tại: `reports/group_report.md`*  
*Commit sau 18:00 được phép theo SCORING.md*
