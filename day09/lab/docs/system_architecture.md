# System Architecture — Lab Day 09

**Nhóm:** [Điền tên nhóm]  
**Ngày:** [Điền ngày nộp]  
**Version:** 1.0

---

## 1. Tổng quan kiến trúc

> Mô tả ngắn hệ thống của nhóm: chọn pattern gì, gồm những thành phần nào.

**Pattern đã chọn:** Supervisor-Worker  
**Lý do chọn pattern này (thay vì single agent):**  

Nhóm lựa chọn pattern Supervisor-Worker vì bài toán không chỉ còn là retrieval đơn thuần như Day 08, mà đã mở rộng sang điều phối nhiều loại xử lý khác nhau như retrieval, policy check, MCP tool calling và human review. Kiến trúc này giúp tách rõ trách nhiệm của từng thành phần, tăng khả năng debug và hỗ trợ mở rộng pipeline về sau mà không cần sửa toàn bộ hệ thống như trong mô hình single-agent.

---

## 2. Sơ đồ Pipeline

> Vẽ sơ đồ pipeline dưới dạng text, Mermaid diagram, hoặc ASCII art.
> Yêu cầu tối thiểu: thể hiện rõ luồng từ input → supervisor → workers → output.

**Sơ đồ thực tế của nhóm:**

```text
User Request
     │
     ▼
┌──────────────┐
│  Supervisor  │
│  - route_reason
│  - risk_high
│  - needs_tool
└──────┬───────┘
       │
   [route_decision]
       │
  ┌────┼───────────────────────────────┐
  │    │                               │
  ▼    ▼                               ▼
Retrieval Worker              Policy Tool Worker            Human Review
(evidence retrieval)          (policy + MCP)               (risk gate / HITL)
  │                                   │                         │
  └───────────────┬───────────────────┴───────────────┬─────────┘
                  │                                   │
                  ▼                                   │
             Synthesis Worker                         │
         (answer + sources + confidence)              │
                  │                                   │
                  └───────────────────────────────────┘
                                  │
                                  ▼
                                Output
```

---

## 3. Vai trò từng thành phần

### Supervisor (`graph.py`)

| Thuộc tính | Mô tả |
|-----------|-------|
| **Nhiệm vụ** | Phân tích task đầu vào và quyết định route sang worker phù hợp |
| **Input** | Câu hỏi từ người dùng (`task`) |
| **Output** | `supervisor_route`, `route_reason`, `risk_high`, `needs_tool` |
| **Routing logic** | Keyword-based routing: policy/access keywords → `policy_tool_worker`; SLA/ticket queries → `retrieval_worker`; mã lỗi rủi ro cao → `human_review` |
| **HITL condition** | Khi `risk_high=True`, đặc biệt với query chứa mã lỗi không rõ như `ERR-...` |

### Retrieval Worker (`workers/retrieval.py`)

| Thuộc tính | Mô tả |
|-----------|-------|
| **Nhiệm vụ** | Retrieve evidence liên quan từ Knowledge Base |
| **Embedding model** | `all-MiniLM-L6-v2` trong trace Day 09 |
| **Top-k** | Placeholder hiện trả evidence retrieval để synthesis sử dụng |
| **Stateless?** | Yes |

### Policy Tool Worker (`workers/policy_tool.py`)

| Thuộc tính | Mô tả |
|-----------|-------|
| **Nhiệm vụ** | Xử lý các câu hỏi thuộc nhóm policy/access và gọi MCP tools nếu cần |
| **MCP tools gọi** | `search_kb`, `get_ticket_info`, `check_access_permission`, `create_ticket` |
| **Exception cases xử lý** | Trường hợp query chứa nhiều tín hiệu policy/access hoặc cần thông tin tool-based thay vì chỉ retrieval thuần |

### Synthesis Worker (`workers/synthesis.py`)

| Thuộc tính | Mô tả |
|-----------|-------|
| **LLM model** | Placeholder trong graph hiện tại; synthesis thực tế được mô phỏng trong worker wrapper |
| **Temperature** | Không nêu rõ trong graph placeholder |
| **Grounding strategy** | Tổng hợp final answer dựa trên chunks/policy result đã được ghi vào shared state |
| **Abstain condition** | Chưa triển khai đầy đủ ở graph placeholder, nhưng có thể mở rộng ở synthesis layer |

### MCP Server (`mcp_server.py`)

| Tool | Input | Output |
|------|-------|--------|
| search_kb | query, top_k | chunks, sources |
| get_ticket_info | ticket_id | ticket details |
| check_access_permission | access_level, requester_role | can_grant, approvers |
| create_ticket | priority, title, description | ticket_id, url, created_at |

---

## 4. Shared State Schema

> Liệt kê các fields trong AgentState và ý nghĩa của từng field.

| Field | Type | Mô tả | Ai đọc/ghi |
|-------|------|-------|-----------|
| task | str | Câu hỏi đầu vào | supervisor đọc |
| supervisor_route | str | Worker được chọn | supervisor ghi |
| route_reason | str | Lý do route | supervisor ghi |
| risk_high | bool | Cờ rủi ro cao | supervisor ghi, human_review đọc |
| needs_tool | bool | Có cần external tool hay không | supervisor ghi |
| hitl_triggered | bool | Có trigger human review hay không | human_review ghi |
| retrieved_chunks | list | Evidence từ retrieval | retrieval ghi, synthesis đọc |
| retrieved_sources | list | Danh sách nguồn evidence | retrieval ghi, synthesis đọc |
| policy_result | dict | Kết quả kiểm tra policy | policy_tool ghi, synthesis đọc |
| mcp_tools_used | list | Tool calls đã thực hiện | policy_tool ghi |
| final_answer | str | Câu trả lời cuối | synthesis ghi |
| sources | list | Sources của câu trả lời | synthesis ghi |
| confidence | float | Mức tin cậy | synthesis ghi |
| history | list | Lịch sử các bước trong pipeline | tất cả các node cập nhật |
| workers_called | list | Danh sách workers đã chạy | các worker ghi |
| latency_ms | int / None | Thời gian xử lý | graph ghi |
| run_id | str | ID của mỗi run | khởi tạo ban đầu |

---

## 5. Lý do chọn Supervisor-Worker so với Single Agent (Day 08)

| Tiêu chí | Single Agent (Day 08) | Supervisor-Worker (Day 09) |
|----------|----------------------|--------------------------|
| Debug khi sai | Khó — không rõ lỗi ở đâu | Dễ hơn — test từng worker độc lập |
| Thêm capability mới | Phải sửa toàn prompt/pipeline | Thêm worker hoặc MCP tool riêng |
| Routing visibility | Không có | Có `route_reason` trong trace |
| Observability | Chỉ thấy answer cuối | Có trace đầy đủ từng bước |
| Human-in-the-loop | Không có tầng riêng | Có thể route sang `human_review` |

**Nhóm điền thêm quan sát từ thực tế lab:**  

Qua trace thực tế, điểm mạnh rõ nhất của Day 09 là khả năng nhìn thấy quyết định route và chuỗi worker đã chạy. Điều này không trực tiếp làm câu trả lời tốt hơn trong mọi trường hợp, nhưng giúp việc kiểm tra, debug và giải thích hành vi hệ thống tốt hơn đáng kể so với Day 08.

---

## 6. Giới hạn và điểm cần cải tiến

> Nhóm mô tả những điểm hạn chế của kiến trúc hiện tại.

1. Routing hiện tại mới dừng ở heuristic theo keyword, chưa đủ mạnh cho các câu multi-hop hoặc câu có ngữ nghĩa phức tạp.
2. Các worker trong `graph.py` vẫn còn nhiều placeholder, nên chưa phản ánh đầy đủ một production pipeline thật.
3. Metrics của Day 09 hiện mạnh về trace và observability nhưng còn thiếu các score chất lượng answer tương đương Day 08 như faithfulness, relevance và completeness.
