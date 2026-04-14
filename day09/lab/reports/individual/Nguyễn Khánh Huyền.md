# Báo Cáo Cá Nhân — Lab Day 09: Multi-Agent Orchestration

**Họ và tên:** Nguyễn Khánh Huyền  
**Vai trò trong nhóm:** Trace & Docs Owner  
**Ngày nộp:** 14.04.2026 
**Độ dài yêu cầu:** 500–800 từ

---

> **Lưu ý quan trọng:**
> - Viết ở ngôi **"tôi"**, gắn với chi tiết thật của phần bạn làm
> - Phải có **bằng chứng cụ thể**: tên file, đoạn code, kết quả trace, hoặc commit
> - Nội dung phân tích phải khác hoàn toàn với các thành viên trong nhóm
> - Deadline: Được commit **sau 18:00** (xem SCORING.md)
> - Lưu file với tên: `reports/individual/[ten_ban].md` (VD: `nguyen_van_a.md`)

---

## 1. Tôi phụ trách phần nào? (100–150 từ)

**Module/file tôi chịu trách nhiệm:**
- File chính: `eval_trace.py`, các file tài liệu trong `docs/` và phần tổng hợp báo cáo
- Functions tôi implement: `analyze_traces()`, phần bổ sung metric mức run như `abstain_rate`, `category_distribution`, và phần chuẩn hóa nội dung cho `system_architecture.md`, `routing_decisions.md`, `single_vs_multi_comparison.md`

Phần việc tôi phụ trách tập trung vào lớp quan sát hệ thống và tài liệu hóa. Cụ thể, tôi kiểm tra lại cấu trúc trace mà `graph.py` sinh ra, đọc log từ `artifacts/traces/`, tổng hợp các chỉ số như routing distribution, average latency, MCP usage rate và HITL rate, sau đó dùng các số liệu này để điền và làm sạch các file markdown của nhóm. Công việc này kết nối trực tiếp với phần của các thành viên khác, vì nếu supervisor, worker hoặc MCP chưa ghi trace đúng format thì phần phân tích và báo cáo không thể hoàn thiện được.

**Bằng chứng (commit hash, file có comment tên bạn, v.v.):**

Bằng chứng rõ nhất là các file `eval_trace.py`, `routing_decisions.md`, `system_architecture.md`, `single_vs_multi_comparison.md` và `group_report.md` đều được cập nhật dựa trên trace thực tế của nhóm, thay vì điền mô tả chung chung.

---

## 2. Tôi đã ra một quyết định kỹ thuật gì? (150–200 từ)

**Quyết định:** Tôi chọn ưu tiên **phân tích trace thật để điền tài liệu**, thay vì điền các metric còn thiếu bằng ước lượng hoặc suy diễn từ kiến trúc.

**Lý do:**

Khi tổng hợp báo cáo Day 09, có một vấn đề xuất hiện rất rõ: hệ thống hiện tại tạo ra hai nhóm metric khác nhau. Day 08 cung cấp scorecard mức answer như faithfulness, relevance, completeness; trong khi Day 09 chủ yếu cung cấp trace-level metrics như `routing_distribution`, `avg_latency_ms`, `mcp_usage_rate`, `hitl_rate`. Nếu trộn lẫn hai hệ đo này mà không kiểm tra nguồn gốc, báo cáo sẽ dễ có những con số không khớp với code thực tế. Vì vậy, tôi chủ động chọn cách bám chặt vào output của `eval_trace.py` và chỉ điền những số liệu có thể truy ngược được từ trace.

**Trade-off đã chấp nhận:**

Trade-off của quyết định này là báo cáo có thể kém “đẹp số” hơn, vì một số ô phải ghi `N/A` hoặc kèm chú thích về hạn chế của metric. Tuy nhiên, đổi lại, nội dung phản ánh trung thực tình trạng hệ thống và không tạo cảm giác thổi phồng kết quả.

**Bằng chứng từ trace/code:**

```text
📊 Trace Analysis:
  total_traces: 15
  routing_distribution:
    retrieval_worker: 8/15 (53%)
    policy_tool_worker: 7/15 (46%)
  avg_confidence: 0.1
  avg_latency_ms: 3494
  mcp_usage_rate: 7/15 (46%)
  hitl_rate: 1/15 (6%)
```

---

## 3. Tôi đã sửa một lỗi gì? (150–200 từ)

**Lỗi:** Metric phân tích ban đầu cho Day 09 bị sai lệch do trace cũ không được dọn và category mapping trong phần phân tích không khớp với dữ liệu test.

**Symptom (pipeline làm gì sai?):**

Khi chạy `eval_trace.py`, số `total_traces` ban đầu lớn hơn `total_questions`, dẫn đến việc average latency và routing distribution bị cộng dồn từ nhiều lần chạy. Đồng thời, các metric như `single_doc_answer_rate`, `multi_hop_answer_rate`, `abstain_correct_rate` bị in ra `N/A`, mặc dù dataset test thực tế có category `multi-hop` và `insufficient context`.

**Root cause (lỗi nằm ở đâu — indexing, routing, contract, worker logic?):**

Root cause không nằm ở retrieval hay routing logic, mà nằm ở lớp phân tích: `analyze_traces()` đọc toàn bộ file JSON trong `artifacts/traces` mà không phân biệt lần chạy; còn phần phân tích category lại dùng taxonomy khác với category thật trong `test_questions.json`.

**Cách sửa:**

Tôi dọn trace cũ trước khi chạy lại, sau đó chuẩn hóa cách diễn giải metric trong báo cáo và cập nhật rule phân tích category theo đúng các nhãn đang có như `sla`, `refund`, `access control`, `insufficient context`, `multi-hop`.

**Bằng chứng trước/sau:**
> Dán trace/log/output trước khi sửa và sau khi sửa.

Trước khi làm sạch trace, `total_traces` bị tăng lên 30 dù chỉ chạy 15 câu. Sau khi xóa trace cũ và chạy lại, output trở về đúng:

```text
total_traces: 15
total_questions: 15
```

Điều này giúp các metric trace-level trở nên nhất quán và có thể dùng cho báo cáo.

---

## 4. Tôi tự đánh giá đóng góp của mình (100–150 từ)

**Tôi làm tốt nhất ở điểm nào?**

Tôi làm tốt nhất ở khâu kiểm tra tính nhất quán giữa code, trace và tài liệu. Cụ thể, tôi có thể nhìn ra khá nhanh khi một metric không thực sự đến từ code hoặc khi một file markdown đang mô tả hệ thống theo cách không khớp với log thực tế.

**Tôi làm chưa tốt hoặc còn yếu ở điểm nào?**

Điểm còn yếu là phần triển khai logic lõi của worker. Tôi chủ yếu làm ở lớp review, cleanup và documentation, nên mức độ can thiệp trực tiếp vào retrieval/policy worker thấp hơn các thành viên phụ trách phần core.

**Nhóm phụ thuộc vào tôi ở đâu?** _(Phần nào của hệ thống bị block nếu tôi chưa xong?)_

Nếu phần trace analysis và tài liệu chưa hoàn tất, nhóm vẫn có thể chạy pipeline, nhưng sẽ rất khó hoàn thiện báo cáo, so sánh Day 08 vs Day 09 và chứng minh quyết định kỹ thuật bằng dữ liệu thật.

**Phần tôi phụ thuộc vào thành viên khác:** _(Tôi cần gì từ ai để tiếp tục được?)_

Tôi phụ thuộc trực tiếp vào phần supervisor, worker và MCP implementation của các thành viên khác, vì nếu trace không được ghi đúng hoặc worker chỉ trả output lỗi, tôi không thể tổng hợp metric và hoàn thiện tài liệu một cách có cơ sở.

---

## 5. Nếu có thêm 2 giờ, tôi sẽ làm gì? (50–100 từ)

Nếu có thêm 2 giờ, tôi sẽ hoàn thiện phần evaluation cho Day 09 bằng cách sửa dứt điểm category mapping và bổ sung một metric answer-level đơn giản cho `multi-hop` và `insufficient context`. Lý do là trace hiện đã đủ sạch để phân tích routing, nhưng các metric như `single_doc_answer_rate`, `multi_hop_answer_rate` và `abstain_correct_rate` vẫn chưa phản ánh được test set thực tế do mismatch giữa taxonomy trong code và category trong dữ liệu.

---