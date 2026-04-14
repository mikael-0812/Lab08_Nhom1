# Báo Cáo Nhóm — Lab Day 09: Multi-Agent Orchestration

**Tên nhóm:** [Điền tên nhóm]  
**Thành viên:**
| Tên | Vai trò | Email |
|-----|---------|-------|
| Phạm Hải Đăng | Supervisor Owner | ___ |
| Đào Quang Thắng | Worker Owner | ___ |
| Phạm Hoàng Kim Liên | MCP Owner | ___ |
| Nguyễn Khánh Huyền | Trace & Docs Owner | ___ |

**Ngày nộp:** 14.04.2026  
**Repo:** https://github.com/mikael-0812/Lab08_Nhom1.git  
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

**Hệ thống tổng quan:**

Nhóm xây dựng hệ thống theo pattern **Supervisor–Worker**, trong đó `graph.py` đóng vai trò điều phối trung tâm. Pipeline bắt đầu từ câu hỏi đầu vào, sau đó supervisor phân tích nội dung câu hỏi và gán các cờ như `supervisor_route`, `route_reason`, `risk_high`, `needs_tool`. Tùy theo quyết định route, hệ thống chuyển sang `retrieval_worker`, `policy_tool_worker` hoặc `human_review`, rồi cuối cùng luôn đi qua `synthesis_worker` để tạo câu trả lời. Bên cạnh đó, `mcp_server.py` cung cấp một lớp tool abstraction để hệ thống có thể mở rộng qua MCP thay vì hard-code trực tiếp logic vào pipeline. Dữ liệu trace từ lần chạy mới nhất của `eval_trace.py` cho thấy routing phân bố tương đối cân bằng giữa `retrieval_worker` (29/59 câu) và `policy_tool_worker` (39/59 câu), với 50% số câu có MCP usage và 5% số câu trigger HITL. Điều này cho thấy kiến trúc của nhóm đã đạt được mục tiêu chính của Lab Day 09 là tách orchestration khỏi retrieval/generation và tăng khả năng quan sát luồng xử lý.

**Routing logic cốt lõi:**
> Mô tả logic supervisor dùng để quyết định route (keyword matching, LLM classifier, rule-based, v.v.)

Supervisor hiện sử dụng **rule-based routing theo keyword**. Các từ khóa thuộc nhóm policy/access như `refund`, `license`, `cấp quyền`, `level 3` sẽ route sang `policy_tool_worker`. Các câu hỏi thiên về SLA, ticket hoặc knowledge retrieval mặc định đi vào `retrieval_worker`. Với các trường hợp rủi ro cao như mã lỗi không rõ dạng `ERR-...`, supervisor gắn `risk_high=True` và route sang `human_review` trước khi tiếp tục pipeline.

**MCP tools đã tích hợp:**
> Liệt kê tools đã implement và 1 ví dụ trace có gọi MCP tool.

- `search_kb`: Dùng để tìm kiếm tri thức nội bộ theo query và trả về top-k chunks liên quan.
- `get_ticket_info`: Dùng để tra cứu mock ticket, ví dụ `P1-LATEST` hoặc `IT-1234`.
- `check_access_permission`: Dùng để kiểm tra khả năng cấp quyền theo access level, requester role và emergency flag.
- `create_ticket`: Dùng để tạo mock ticket phục vụ workflow mô phỏng.

Ví dụ trace có gọi MCP tool là các câu thuộc nhóm refund hoặc access control; tổng cộng 7/15 câu trong test run có `mcp_usage_rate = 50%`.

---

## 2. Quyết định kỹ thuật quan trọng nhất (200–250 từ)

**Quyết định:** Chọn **Supervisor–Worker với rule-based routing** thay vì cố gắng xây một single-agent hoặc classifier-based router ngay từ đầu.

**Bối cảnh vấn đề:**

Bài toán của lab không còn chỉ là retrieval đơn giản như Day 08. Hệ thống cần phân biệt giữa nhiều loại query: query tra cứu SLA, query về policy/refund, query access control, query có mã lỗi cần xử lý thận trọng, và các câu có thể cần external tool qua MCP. Nếu tất cả được nhồi vào một pipeline đơn, việc debug và mở rộng sẽ rất khó. Vì vậy, nhóm phải quyết định nên giữ kiến trúc đơn giản hay chuyển sang một lớp supervisor để điều phối.

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|-----------|
| Single-agent mở rộng từ Day 08 | Dễ triển khai nhanh, ít thành phần | Khó debug, khó thêm tool, không có routing visibility |
| Supervisor–Worker + heuristic routing | Rõ luồng xử lý, dễ mở rộng, dễ trace | Cần thêm orchestration layer, có overhead, routing chỉ là heuristic |

**Phương án đã chọn và lý do:**

Nhóm chọn phương án thứ hai: **Supervisor–Worker với heuristic routing**. Lý do chính không phải vì nó chắc chắn tăng chất lượng answer ở mọi câu hỏi, mà vì nó giúp hệ thống có cấu trúc rõ ràng hơn, dễ debug hơn và phù hợp với yêu cầu của Lab Day 09. Với thời gian hạn chế, keyword-based routing là mức phức tạp hợp lý: dễ kiểm soát, dễ giải thích, và đủ để đi đến một bản pipeline hoạt động được end-to-end.

**Bằng chứng từ trace/code:**
> Dẫn chứng cụ thể (VD: route_reason trong trace, đoạn code, v.v.)

```text
Query: ERR-403-AUTH là lỗi gì và cách xử lý?
route_reason: unknown error code + risk_high → human review
workers_called: human_review -> retrieval_worker -> synthesis_worker
```

Ví dụ này cho thấy routing không còn là một khối mờ như Day 08, mà có thể được quan sát và giải thích trực tiếp từ trace.

---

## 3. Kết quả grading questions (150–200 từ)

**Tổng điểm raw ước tính:** N/A / 96

**Câu pipeline xử lý tốt nhất:**
- ID: Chưa có grading file thực tế — Lý do tốt: Hiện nhóm mới có test run trên `test_questions.json`, chưa có số liệu chính thức từ `grading_questions.json`.

**Câu pipeline fail hoặc partial:**
- ID: N/A — Fail ở đâu: Chưa có grading log chính thức  
  Root cause: Chưa có file `grading_questions.json` thực tế trong dữ liệu hiện tại, nên không thể báo cáo raw score một cách trung thực.

**Câu gq07 (abstain): Nhóm xử lý thế nào?**

Về mặt thiết kế, nhóm đã chuẩn bị nhánh `human_review` cho các trường hợp rủi ro cao hoặc thiếu ngữ cảnh, đặc biệt với query chứa mã lỗi không rõ. Tuy nhiên, ở implementation hiện tại của Day 09, `graph.py` vẫn đang dùng worker wrappers/placeholder nên answer-level abstain chưa được triển khai hoàn chỉnh như Day 08. Vì vậy, với grading question dạng abstain, hướng xử lý đúng là route thận trọng ở tầng supervisor trước, nhưng hành vi abstain cuối cùng vẫn cần hoàn thiện thêm ở synthesis layer.

**Câu gq09 (multi-hop khó nhất): Trace ghi được 2 workers không? Kết quả thế nào?**

Với các query phức tạp chứa đồng thời tín hiệu policy và incident/access, trace đã cho thấy khả năng route sang `policy_tool_worker`, sau đó tiếp tục đi qua retrieval và synthesis. Điều này chứng minh supervisor-worker pattern đã hỗ trợ ít nhất một dạng multi-step flow, dù chất lượng answer cuối cùng còn phụ thuộc vào việc hoàn thiện worker thật thay vì placeholder.

---

## 4. So sánh Day 08 vs Day 09 — Điều nhóm quan sát được (150–200 từ)

**Metric thay đổi rõ nhất (có số liệu):**

Metric thay đổi rõ nhất là **routing visibility và trace observability**. Ở Day 08, hệ thống chủ yếu cho ra answer cuối, còn Day 09 bổ sung thêm `supervisor_route`, `route_reason`, `workers_called`, `hitl_triggered`, `mcp_tools_used` và `latency_ms` trong trace. Về số liệu thực tế, Day 09 có `avg_latency_ms = 9637`, `mcp_usage_rate = 50%`, `hitl_rate = 5%`, và routing phân bố 49% retrieval / 50% policy. Trong khi đó, Day 08 mạnh hơn ở answer-level scorecard như `faithfulness = 5.00`, `relevance = 4.40`, `completeness = 3.40`, nhưng chưa có một lớp orchestration rõ ràng.

**Điều nhóm bất ngờ nhất khi chuyển từ single sang multi-agent:**

Điều bất ngờ nhất là multi-agent không tự động làm answer tốt hơn trong mọi trường hợp. Lợi ích lớn nhất của Day 09 nằm ở khả năng phân tách trách nhiệm và debug luồng xử lý, chứ không nhất thiết ở việc mọi metric chất lượng đều tăng lên ngay lập tức.

**Trường hợp multi-agent KHÔNG giúp ích hoặc làm chậm hệ thống:**

Với các câu hỏi đơn giản, một bước retrieval duy nhất thường đã đủ. Trong các trường hợp này, thêm supervisor và routing layer làm pipeline phức tạp hơn mà không đem lại cải thiện rõ về answer quality. Ngoài ra, metric abstain của Day 09 hiện cũng cần được diễn giải thận trọng vì synthesis layer vẫn còn placeholder.

---

## 5. Phân công và đánh giá nhóm (100–150 từ)

**Phân công thực tế:**

| Thành viên | Phần đã làm | Sprint |
|------------|-------------|--------|
| Phạm Hải Đăng | Thiết kế supervisor và graph orchestration | Sprint 1 |
| Đào Quang Thắng | Implement workers và kiểm tra retrieval/policy flow | Sprint 2 |
| Phạm Hoàng Kim Liên | MCP server, tool schemas và dispatch logic | Sprint 3 |
| Nguyễn Khánh Huyền | Trace analysis, docs, report và merge code | Sprint 4 |

**Điều nhóm làm tốt:**

Nhóm phối hợp tốt ở khâu chia nhỏ bài toán theo module, giúp mỗi phần có thể được triển khai và kiểm tra độc lập. Việc có trace JSON cũng hỗ trợ nhiều cho quá trình review và merge.

**Điều nhóm làm chưa tốt hoặc gặp vấn đề về phối hợp:**

Một hạn chế là có thời điểm các phần được hoàn thành không đồng bộ, dẫn đến việc graph chạy được nhưng worker hoặc metric vẫn còn placeholder. Điều này làm cho một số answer-level metric của Day 09 chưa phản ánh đúng chất lượng hệ thống cuối cùng.

**Nếu làm lại, nhóm sẽ thay đổi gì trong cách tổ chức?**

Nếu làm lại, nhóm nên chốt rõ interface giữa các worker sớm hơn và thống nhất luôn format output/trace ngay từ đầu, để giảm công sức cleanup và merge ở cuối.

---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì? (50–100 từ)

Nếu có thêm một ngày, nhóm sẽ ưu tiên hoàn thiện ba hướng: (1) thay các placeholder workers bằng implementation thật, đặc biệt ở synthesis layer để hỗ trợ abstain và grounded answer tốt hơn; (2) bổ sung metric tự động cho multi-hop accuracy và abstain rate trong Day 09; và (3) chuẩn hóa category mapping trong evaluation để các chỉ số answer-level phản ánh đúng hơn hiệu quả thực tế của supervisor-worker pipeline.

---

*File này lưu tại: `reports/group_report.md`*  
*Commit sau 18:00 được phép theo SCORING.md*
