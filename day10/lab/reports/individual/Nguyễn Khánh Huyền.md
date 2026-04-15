# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Nguyễn Khánh Huyền  
**Vai trò:** Review code và kiểm tra kết quả pipeline / eval / grading  
**Ngày nộp:** 2026-04-15  

---

## 1. Tôi phụ trách phần nào?

Trong Lab Day 10, phần việc chính của tôi không phải là viết mới pipeline mà là đọc lại code, kiểm tra logic chạy end-to-end và đối chiếu kết quả đầu ra giữa các bước clean, validate, embed và retrieval evaluation. Tôi tập trung vào các file `etl_pipeline.py`, `eval_retrieval.py`, `grading_run.py` và `instructor_quick_check.py` để xác nhận pipeline có chạy đúng luồng ingest → clean → validate → embed, sau đó dùng các file eval để kiểm tra chất lượng dữ liệu sau khi làm sạch. `etl_pipeline.py` cho thấy pipeline tạo `run_id`, ghi log, sinh cleaned CSV, quarantine CSV, chạy expectation rồi mới embed vào ChromaDB; ngoài ra còn ghi manifest và freshness check ở cuối run. `eval_retrieval.py` và `grading_run.py` được dùng để đo kết quả truy xuất sau khi re-embed dữ liệu, còn `instructor_quick_check.py` dùng để sanity check file `grading_run.jsonl` theo các tiêu chí chấm nhanh của giảng viên.

Phần việc của tôi kết nối với các bạn trong nhóm ở chỗ: sau khi các bạn hoàn thiện cleaning rules, expectations và phần embedding, tôi là người kiểm tra xem kết quả chạy có nhất quán với mục tiêu của bài lab hay không, đặc biệt ở before/after retrieval. Nội dung này cũng khớp với khung nhóm trong `group_report.md`, nơi phần before/after tập trung vào việc phát hiện chunk stale và xác nhận retrieval đã sạch hơn sau khi chạy pipeline chuẩn.
---

## 2. Một quyết định kỹ thuật

Quyết định kỹ thuật mà tôi thấy quan trọng nhất trong lab này là tách riêng bước **validate** khỏi bước **embed**, đồng thời cho phép pipeline chọn giữa hai chế độ: dừng hẳn khi expectation fail hoặc tiếp tục chạy để phục vụ demo có chủ đích. Trong `etl_pipeline.py`, sau khi dữ liệu được clean, hàm `run_expectations(cleaned)` trả về `results, halt`; nếu `halt` và không bật `--skip-validate` thì pipeline ghi log `PIPELINE_HALT` và dừng, còn nếu có `--skip-validate` thì pipeline vẫn tiếp tục embed nhưng có cảnh báo rõ ràng. Cách thiết kế này hợp lý vì trong điều kiện bình thường, dữ liệu lỗi phải chặn trước khi publish vào vector store; nhưng trong bối cảnh bài lab, nhóm vẫn cần một chế độ “inject bad data” để chứng minh tác động của dữ liệu bẩn lên retrieval.

Từ góc độ review, tôi đánh giá đây là lựa chọn tốt vì vừa giữ được tính an toàn mặc định của pipeline, vừa hỗ trợ thực nghiệm before/after một cách minh bạch. Nó cũng làm cho việc đọc kết quả dễ hơn: nếu retrieval xấu sau một run, tôi có thể kiểm tra lại ngay run đó có dùng `--skip-validate` hoặc `--no-refund-fix` hay không thay vì phải suy đoán từ output cuối.

---

## 3. Một lỗi hoặc anomaly đã xử lý

Anomaly rõ nhất mà tôi theo dõi trong phần review là trường hợp dữ liệu stale về chính sách refund vẫn lọt vào retrieval top-k khi nhóm cố ý chạy chế độ inject. Trong phần mô tả của báo cáo nhóm, kịch bản này xảy ra khi pipeline chạy với `--no-refund-fix --skip-validate`, làm cho chunk chứa thông tin cũ “14 ngày làm việc” vẫn được embed vào ChromaDB. Khi đó, metric `hits_forbidden` của câu hỏi liên quan đến refund chuyển thành `yes`, nghĩa là top-k retrieval vẫn còn chứa nội dung không mong muốn. Sau khi chạy lại pipeline chuẩn, rule sửa refund 14→7 ngày được áp dụng, đồng thời bước prune ở embed xóa vector stale khỏi collection. Khi đó kết quả retrieval trở về trạng thái sạch hơn, với `hits_forbidden=no`. 

Tôi không trực tiếp sửa cleaning rule này, nhưng phần tôi làm là kiểm tra xem anomaly có thực sự phản ánh lên output hay không. Để làm việc đó, tôi đọc logic của `eval_retrieval.py`: chương trình query Chroma collection, ghép các document top-k thành một blob rồi kiểm tra `must_contain_any` và `must_not_contain`. Nhờ vậy, tôi có thể xác nhận rằng lỗi không chỉ nằm ở mặt mô tả trong báo cáo mà đã được phản ánh thành metric cụ thể ở file eval. Ngoài ra, `instructor_quick_check.py` còn có các điều kiện kiểm tra `contains_expected`, `hits_forbidden` và riêng một số câu còn yêu cầu `top1_doc_matches`, giúp việc rà soát đầu ra khách quan hơn.
---

## 4. Bằng chứng trước / sau

Bằng chứng before/after mà tôi dùng để kiểm tra kết quả là sự thay đổi của metric ở câu hỏi refund window trong báo cáo nhóm. Ở run inject-bad, kết quả là `contains_expected = yes` nhưng `hits_forbidden = yes`, tức là hệ thống có truy xuất được thông tin liên quan nhưng vẫn lẫn chunk sai. Sau khi chạy lại bằng pipeline chuẩn `final-clean`, kết quả trở thành `contains_expected = yes` và `hits_forbidden = no`. Đây là thay đổi quan trọng nhất vì nó cho thấy cleaning không chỉ làm dữ liệu “đẹp hơn” mà thực sự cải thiện chất lượng retrieval. Báo cáo nhóm cũng ghi rõ thêm rằng trong run sạch, bước embed prune đã loại bỏ vector stale, nên before/after không chỉ là khác biệt trong text mà là khác biệt ở chính collection đã publish.

---

## 5. Cải tiến tiếp theo

Nếu có thêm khoảng 2 giờ, tôi muốn bổ sung một file tổng hợp kết quả review tự động, ví dụ `review_summary.md` hoặc một script nhỏ đọc `before_after_eval.csv`, `grading_run.jsonl` và manifest rồi in ra các chỉ số quan trọng theo từng `run_id`. Như vậy phần kiểm tra của reviewer sẽ nhanh hơn, đỡ phải mở nhiều artifact rời rạc để đối chiếu thủ công.