# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Pham Hoang Kim Lien
**Vai trò:** Cleaning / Quality Owner | `cleaning_rules.py`, `expectations.py`, quarantine
**Ngày nộp:** 2026-04-15
**Độ dài yêu cầu:** **400–650 từ**

---

## 1. Tôi phụ trách phần nào? (80–120 từ)

**File / module:**
- `transform/cleaning_rules.py`: Chịu trách nhiệm thiết lập các quy tắc làm sạch (cleaning rules) dữ liệu. Tôi đã bổ sung 3 quy tắc mới: loại bỏ ký tự zero-width/BOM, chuẩn hoá các cụm whitespace để làm gọn văn bản, và quarantine những chunk rác (có ít hơn 10 ký tự chữ và số).
- `quality/expectations.py`: Cấu hình các bộ luật kiểm định (expectations) chất lượng dữ liệu để chốt chặn trước khi lưu vào DB. Tôi cập nhật luật E7 kiểm tra tính duy nhất của `chunk_id` (sẽ halt nếu bị trùng) và luật E8 để đưa ra cảnh báo (warn) nếu bất kỳ ký tự zero-width nào lọt qua khâu làm sạch.
- Xem xét đầu ra `quarantine`: Theo dõi và đánh giá danh sách các nội dung bị cách ly qua từng đợt chạy để đảm bảo chất lượng file CSV đầu ra.

**Kết nối với thành viên khác:**
Dữ liệu mà tôi xử lý và làm sạch thành công ở luồng này là nền tảng cốt lõi đưa cho khâu Embed (chịu trách nhiệm vector hoá). Việc loại bỏ khoảng trắng rác, các ký tự không xuất hiện (zero-width) và loại trừ nội dung ngắn không có ý nghĩa sẽ phòng tránh tình trạng khâu Embed tạo ra những chunk không có giá trị, qua đó nâng cao chất lượng RAG cho thành viên Agent.

**Bằng chứng (commit / comment trong code):**
Đoạn mã:
```python
        # ── Rule mới R3: Minimum meaningful content ──
        _alphanum_only = re.sub(r"[^a-zA-Z0-9\u00C0-\u024F\u1E00-\u1EFF]", "", fixed_text)
        if len(_alphanum_only) < 10:
            quarantine.append({**raw, "reason": "insufficient_meaningful_content"})
            continue
```

---

## 2. Một quyết định kỹ thuật (100–150 từ)

Tôi quyết định sử dụng mức độ `halt` (dừng toàn bộ pipeline) đối với bộ kiểm tra tính duy nhất của `chunk_id` (Expectation E7). Lý do: trong hệ thống cơ sở dữ liệu Vector (như ChromaDB), thuộc tính `chunk_id` được dùng làm khoá định danh chính khi thực hiện các phép upsert (cập nhật hoặc chèn mới) chunk nhúng vào DB. Nếu hàm xuất trả về các `chunk_id` bị lặp, các mảnh dữ liệu sau sẽ vô căn cứ ghi đè hoặc tạo ra xung đột với nội dung của đoạn tài liệu trước đó, dẫn đến mất dữ liệu và giảm mức độ chính xác của tài liệu. Gán `halt` giúp hệ thống dừng sớm (fail-fast), thay vì chỉ `warn` rồi để mặc lỗi lan tới Vector Store. Với luật BOM/zero-width (Expectation E8), việc tôi không cho dừng luồng (chỉ `warn`) là do những ký tự này thường chỉ gây lỗi hiển thị (render) nhẹ chứ không gây sụp đổ logic hay hư hại DB nặng nề như vậy.

---

## 3. Một lỗi hoặc anomaly đã xử lý (100–150 từ)

Triệu chứng: Khi kiểm tra chất lượng ban đầu phân khúc thô xuất từ các tệp hỗn hợp, tôi phát hiện một số chunk được khai báo `chunk_text` hoàn toàn không hữu dụng để RAG nhưng vẫn đi lọt qua đoạn kiểm tra rỗng (`if not text`) cơ bản.
Phát hiện: Phân tích kỹ thuật phát hiện rằng nội dung bên trong chứa rải rác các escape character, các ký hiệu độ rộng bằng 0 (`zero-width` như `\ufeff`), và các cụm tab khoảng trắng biến thể. Những chuỗi này đối với máy tính lớn hơn 0 độ dài, nhưng với bộ não LLM là sự lãng phí thông tin (junk metrics).
Giải pháp xử lý: Tôi thiết kế `cleaning_rules` lại thành một chuỗi hai lớp. Lớp thứ nhất (Rule R1+R2) tước sạch các zero-width character cũng như thu vén khoảng trắng (collapse whitespace). Lớp khắt khe thứ 2 (Rule R3) chỉ gạn lọc bảng chữ cái và số (alphanumeric), khi kích thước nhỏ hơn 10 ký tự, tôi lập tức tiễn nó vào file quarantine với nhãn lỗi `"insufficient_meaningful_content"`. Lỗi triệt để được loại bỏ.

---

## 4. Bằng chứng trước / sau (80–120 từ)

Tôi đã chạy kiểm thử để validate các behavior của việc làm sạch và chặn chặn này với các run-id phân biệt.

Trước tiên đối với Expectation E7, nếu tôi mô phỏng inject một lỗi duplicate chunk:
Quá trình Pipeline lập tức `FAIL` và log `halt`:
`ExpectationResult(name='unique_chunk_id', passed=False, severity='halt', detail='duplicate_chunk_ids=2')`
Điều này đảm bảo DB sẽ không nhận cập nhật lỗi.

Bằng chứng Quarantine thành công loại bỏ rác từ Rule R3:
Sau lần càn quét `clean_rows`, tôi xem trong mục file `artifacts/quarantine/quarantine_first-clean.csv`, nội dung bị bắt rõ ràng, chẳng hạn:
```csv
chunk_id,doc_id,... reason
...,hr_leave_policy,... insufficient_meaningful_content
```
Qua đó chứng minh Pipeline vừa chủ động làm sạch rác, vừa chặn dữ liệu sai cấu trúc đe doạ bảo toàn tính toàn vẹn của Vector Store phía sau.

---

## 5. Cải tiến tiếp theo (40–80 từ)

Nếu có thêm thời gian (khoảng 2 giờ), tôi sẽ thực hiện refactor bộ `Expectations.py` bằng việc áp dụng thư viện chuẩn công nghiệp như `Great Expectations` (GE) hay `Pydantic` validation. Việc sử dụng GE không chỉ cung cấp sẵn các Assertions chuẩn về cấu trúc dữ liệu, mà còn sinh ra Data Docs (tài liệu HTML trực quan) - báo cáo chất lượng data sẽ đẹp và dễ đọc hơn nhiều cho mọi thành viên nhóm so với chuỗi in terminal logs như chức năng thủ công hiện tại.