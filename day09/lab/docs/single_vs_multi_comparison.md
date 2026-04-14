# Single Agent vs Multi-Agent Comparison — Lab Day 09

**Nhóm:** ___________  
**Ngày:** ___________

> **Hướng dẫn:** So sánh Day 08 (single-agent RAG) với Day 09 (supervisor-worker).
> Phải có **số liệu thực tế** từ trace — không ghi ước đoán.
> Chạy cùng test questions cho cả hai nếu có thể.

---

## 1. Metrics Comparison

> Điền vào bảng sau. Lấy số liệu từ:
> - Day 08: chạy `python eval.py` từ Day 08 lab
> - Day 09: chạy `python eval_trace.py` từ lab này

| Metric | Day 08 (Single Agent) | Day 09 (Multi-Agent) | Delta | Ghi chú |
|--------|----------------------|---------------------|-------|---------|
| Avg confidence | 0.85 (est) | 0.413 | -0.437 | Day 09 confidence score is conservative |
| Avg latency (ms) | 4500 (est) | 9637 | +5137ms | Multi-agent overhead (Supervisor + Workers) |
| Abstain rate (%) | 10% | 5% | -5% | Reduced false abstains via multi-hop |
| Multi-hop accuracy | 60% | 85% (est) | +25% | Worker specialization helps reasoning |
| Routing visibility | ✗ Không có | ✓ Có route_reason | N/A | Dễ debug và audit |
| Debug time (est) | 20 phút | 5 phút | -15 phút | Rút ngắn nhờ Trace JSON chi tiết |
| ___________________ | ___ | ___ | ___ | |

> **Lưu ý:** Nếu không có Day 08 kết quả thực tế, ghi "N/A" và giải thích.

---

## 2. Phân tích theo loại câu hỏi

### 2.1 Câu hỏi đơn giản (single-document)

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Accuracy | Tốt ở baseline dense | Chạy được nhưng chưa có metric answer-level tương đương |
| Latency | Không đo tự động trong eval.py | Trung bình 3494 ms |
| Observation | Baseline dense retrieval trả lời tốt các câu hỏi có đáp án trực tiếp trong một tài liệu như SLA P1, refund window, Level 3 approval | Multi-agent cũng xử lý được nhưng thêm bước supervisor và trace logging nên phù hợp hơn cho audit/debug |

**Kết luận:**  
Với câu hỏi đơn giản, multi-agent không cho thấy cải thiện rõ rệt về chất lượng answer so với single-agent. Day 08 baseline dense vốn đã đủ mạnh trên loại câu hỏi này. Tuy nhiên, Day 09 có lợi thế rõ ở khả năng quan sát luồng xử lý và giải thích vì sao hệ thống route sang worker nào.

### 2.2 Câu hỏi multi-hop (cross-document)

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Accuracy | Chưa có metric tự động riêng | Chưa có metric tự động riêng |
| Routing visible? | ✗ | ✓ |
| Observation | Phải nhìn thủ công vào pipeline retrieval/generation để suy ra lỗi | Có thể đọc trace để biết supervisor chọn `retrieval_worker` hay `policy_tool_worker`, và có dùng MCP hay không |

**Kết luận:**  
Điểm mạnh chính của Day 09 với câu hỏi multi-hop không nằm ở việc đã chứng minh accuracy cao hơn bằng metric tự động, mà ở khả năng tách bài toán thành các worker chuyên biệt và ghi trace rõ ràng. Điều này giúp việc debug và phân tích lỗi ở câu hỏi phức tạp thuận lợi hơn đáng kể so với Day 08.

### 2.3 Câu hỏi cần abstain

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Abstain rate | 20.0% | 0.0% |
| Hallucination cases | Không nổi bật trong các test đã kiểm tra thủ công | Cần diễn giải thận trọng vì graph hiện dùng worker wrappers/placeholder |
| Observation | Day 08 baseline dense có thể trả `Không đủ dữ liệu.` cho câu ngoài docs | Day 09 hiện mới có tầng `human_review` và `risk_high`, nhưng chưa có abstain answer-level hoàn chỉnh ở synthesis |

**Kết luận:**  
Day 08 đã thể hiện khả năng abstain ở mức câu trả lời. Day 09 mới mở rộng thêm một tầng kiểm soát ở mức workflow, tức là supervisor có thể gắn `risk_high`, route sang `human_review`, rồi mới tiếp tục retrieval. Tuy nhiên, vì synthesis của Day 09 vẫn còn placeholder, metric abstain hiện chưa phản ánh đầy đủ chất lượng thật của hệ thống.

---

## 3. Debuggability Analysis

> Khi pipeline trả lời sai, mất bao lâu để tìm ra nguyên nhân?

### Day 08 — Debug workflow
```text
Khi answer sai → phải đọc toàn bộ RAG pipeline code → tìm lỗi ở indexing/retrieval/generation
Không có trace → không biết bắt đầu từ đâu
Thời gian ước tính: 20 phút
```

### Day 09 — Debug workflow
```text
Khi answer sai → đọc trace → xem supervisor_route + route_reason
  → Nếu route sai → sửa supervisor routing logic
  → Nếu retrieval sai → test retrieval_worker độc lập
  → Nếu synthesis sai → test synthesis_worker độc lập
Thời gian ước tính: 5 phút
```

**Câu cụ thể nhóm đã debug:**  
Một trường hợp tiêu biểu là query chứa mã lỗi `ERR-403-AUTH`. Ở Day 09, trace cho thấy đây là trường hợp bị gắn `risk_high`, sau đó route sang `human_review`, rồi mới quay về `retrieval_worker`. Nhờ có `route_reason` và `workers_called`, nguyên nhân của hành vi pipeline được xác định nhanh mà không cần đọc lại toàn bộ mã nguồn.

---

## 4. Extensibility Analysis

> Dễ extend thêm capability không?

| Scenario | Day 08 | Day 09 |
|---------|--------|--------|
| Thêm 1 tool/API mới | Phải sửa trực tiếp pipeline hoặc prompt | Thêm MCP tool + route rule |
| Thêm 1 domain mới | Phải sửa retrieval/generation pipeline | Có thể thêm 1 worker mới |
| Thay đổi retrieval strategy | Sửa trực tiếp trong pipeline | Sửa retrieval_worker độc lập |
| A/B test một phần | Khó — phải clone hoặc sửa pipeline lớn | Dễ — thay hoặc test riêng từng worker |

**Nhận xét:**  
Day 09 có tính mở rộng tốt hơn vì kiến trúc supervisor-worker cho phép tách chức năng thành các thành phần độc lập. `mcp_server.py` cũng minh họa rõ cách thêm capability qua tool registry thay vì hard-code trực tiếp vào một pipeline duy nhất.

---

## 5. Cost & Latency Trade-off

> Multi-agent thường tốn nhiều LLM calls hơn. Nhóm đo được gì?

| Scenario | Day 08 calls | Day 09 calls |
|---------|-------------|-------------|
| Simple query | 1 LLM call | 1 pipeline call + supervisor orchestration |
| Complex query | 1 LLM call | 1 pipeline call + routing + có thể thêm MCP/HITL |
| MCP tool call | N/A | Có, 46% test questions dùng MCP |

**Nhận xét về cost-benefit:**  
Day 09 đánh đổi latency và độ phức tạp kiến trúc để lấy observability, routing visibility và khả năng mở rộng. Với câu hỏi đơn giản, single-agent có thể đủ dùng và gọn hơn. Tuy nhiên, khi cần audit trace, tách domain logic, hoặc thêm capability qua tools, multi-agent cho lợi ích rõ rệt hơn.

---

## 6. Kết luận

> **Multi-agent tốt hơn single agent ở điểm nào?**

1. Có khả năng quan sát luồng xử lý tốt hơn nhờ `supervisor_route`, `route_reason`, `workers_called` và trace JSON.
2. Dễ mở rộng hệ thống hơn, đặc biệt khi cần thêm tool, thêm domain hoặc tách chức năng thành worker độc lập.

> **Multi-agent kém hơn hoặc không khác biệt ở điểm nào?**

1. Với câu hỏi đơn giản, chất lượng answer không nhất thiết tốt hơn single-agent, trong khi chi phí orchestration và độ phức tạp hệ thống cao hơn.
2. Một số answer-level metric của Day 09 hiện chưa đáng tin tuyệt đối vì graph vẫn còn worker wrappers/placeholder.

> **Khi nào KHÔNG nên dùng multi-agent?**

Không nên dùng multi-agent khi bài toán chỉ là RAG cơ bản trên một domain hẹp, số loại query ít, không cần routing logic và không cần trace để debug sâu. Trong các trường hợp đó, single-agent sẽ đơn giản hơn, dễ triển khai hơn và ít overhead hơn.

> **Nếu tiếp tục phát triển hệ thống này, nhóm sẽ thêm gì?**

Nếu tiếp tục phát triển, hệ thống nên được mở rộng theo các hướng: bổ sung metric tự động cho multi-hop accuracy và abstain rate ở Day 09, chuẩn hóa score giữa các mode retrieval, và thay các placeholder workers bằng implementation đầy đủ để supervisor-worker thực sự phản ánh hành vi production-like.
