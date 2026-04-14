# Tài liệu Hướng dẫn Commit theo Vai trò - Lab Day 09

Tài liệu này hướng dẫn chi tiết cách các thành viên trong nhóm thực hiện commit code lên GitHub để đảm bảo tính chuyên nghiệp và đáp ứng đầy đủ tiêu chí chấm điểm của giảng viên.

---

## 📋 Quy tắc chung cho cả nhóm
*   **Commit Message**: Luôn bao gồm [Vai trò] và [Tên] của bạn. Ví dụ: `feat(worker): implement policy exceptions [An]`
*   **Deadline**: Commit Code trước **18:00**. Sau giờ này chỉ commit báo cáo (Reports).
*   **Git Add**: Chỉ `git add` các file thuộc phạm vi mình phụ trách (tránh conflict nếu không cần thiết).

---

## 1. Supervisor Owner (Vai trò 1)
**Trọng tâm**: Luồng điều phối và Quản lý trạng thái.

| File phụ trách | Nội dung chính cần có |
|----------------|-----------------------|
| `graph.py` | Logic `supervisor_node`, các cạnh (`add_edge`), và state management. |
| `reports/individual/` | Báo cáo về quyết định routing (Keyword vs LLM). |

**Lưu ý quan trọng**:
*   Phải đảm bảo `route_reason` được ghi vào state ngay tại supervisor node.
*   Kiểm tra `AgentState` được truyền đầy đủ qua các Workers.

---

## 2. Worker Owner (Vai trò 2)
**Trọng tâm**: Domain logic (Retrieval, Policy, Synthesis).

| File phụ trách | Nội dung chính cần có |
|----------------|-----------------------|
| `workers/retrieval.py` | Kết nối ChromaDB, trích xuất dữ liệu grounded. |
| `workers/policy_tool.py`| Xử lý ngoại lệ (Flash Sale, Digital Products). |
| `workers/synthesis.py` | Trích dẫn nguồn [tên_file], tính confidence thực tế. |
| `contracts/*.yaml` | Cập nhật `actual_implementation: done`. |
| `reports/individual/` | Giải thích logic xử lý ngoại lệ và grounding. |

**Lưu ý quan trọng**:
*   Mỗi worker phải chạy test độc lập được bằng lệnh `python workers/worker_name.py`.
*   Synthesis worker KHÔNG được bịa đặt thông tin (Anti-hallucination).

---

## 3. MCP Owner (Vai trò 3)
**Trọng tâm**: Công cụ và Tích hợp ngoại vi.

| File phụ trách | Nội dung chính cần có |
|----------------|-----------------------|
| `mcp_server.py` | Ít nhất 2 tools (`search_kb`, `get_ticket_info`). |
| `workers/policy_tool.py`| Phần tích hợp `_call_mcp_tool` và log `mcp_tools_used`. |
| `reports/individual/` | Trình bày thiết kế MCP Interface và lỗi đã sửa. |

**Lưu ý quan trọng**:
*   Đảm bảo `mcp_tools_used` ghi lại đầy đủ input/output của tool trong trace log.
*   Công cụ `search_kb` nên kết nối trực tiếp với DB thực của Retrieval Worker.

---

## 4. Trace & Docs Owner (Vai trò 4)
**Trọng tâm**: Đánh giá kết quả và Báo cáo nhóm.

| File phụ trách | Nội dung chính cần có |
|----------------|-----------------------|
| `eval_trace.py` | Script chạy 15 test questions và grading questions. |
| `docs/` | 3 tài liệu: Architecture, Routing, Comparison. |
| `reports/group_report.md`| Phân tích hiệu năng Single vs Multi-agent. |
| `artifacts/traces/` | Các bản ghi JSON thực tế sau khi chạy pipeline. |
| `reports/individual/` | Trình bày cách phân tích data từ các bản trace. |

**Lưu ý quan trọng**:
*   Dữ liệu trong so sánh phải là **Số liệu thực tế** từ trace, không ước đoán.
*   Đảm bảo group report có đầy đủ sơ đồ pipeline (Mermaid).

---
*Tài liệu này được soạn để hỗ trợ nhóm nộp bài Lab Day 09.*
