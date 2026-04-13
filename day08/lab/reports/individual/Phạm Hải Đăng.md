# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Phạm Hải Đăng  
**Vai trò trong nhóm:** Eval Owner  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Trong nhóm, tôi đảm nhận vai trò **Eval Owner** phụ trách đánh giá chất lượng của toàn bộ hệ thống RAG Pipeline (Sprint 3 & 4). Cụ thể, tôi đã thiết kế và tùy chỉnh 10 câu hỏi test (file `test_questions.json`) với đầy đủ expected answers và sources để phủ nhiều trường hợp khác nhau (hỏi về SLA, hoàn tiền, exception, đổi tên tài liệu). 
Tôi cài đặt bộ thư viện chấm điểm sử dụng LLM-as-a-judge trong `eval.py` dựa trên 4 metric quan trọng (Faithfulness, Relevance, Recall và Completeness). Từ đó, tôi chạy scorecard so sánh A/B test giữa Baseline (Dense) và Variant (Hybrid + Rerank) của nhóm, ghi log đánh giá tự động ra các file `results/scorecard_*.md` và `logs/grading_run.json`. Công việc của tôi cung cấp những cơ sở và bằng chứng số liệu trực tiếp để Tech Lead và Retrieval Owner có thể tinh chỉnh các tham số chunk size, overlap, và trọng số của Hybrid Search, từ đó nâng điểm toàn hệ thống lên đáng kể.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Qua việc trực tiếp viết các prompt cho mô hình LLM-as-a-judge (chấm tự động điểm thay vì thủ công), tôi hiểu rõ hơn cách đánh giá hệ thống RAG mà không bị phụ thuộc vào tính chủ quan của con người. Đặc biệt là metric **Context Recall** và **Faithfulness**. 
Trước đây, tôi thường nhầm lẫn giữa câu trả lời đúng (bởi vì bản thân LLM đã biết) và câu trả lời đúng từ context (Faithfulness). Tôi nhận ra rằng ngay cả khi Generation sinh ra một đáp án chính xác về mặt kiến thức, nhưng nếu Retrieval Owner không cung cấp chunk chứa nội dung đó, pipeline vẫn đánh giá là điểm Faithfulness thấp (do lỗi Hallucination ngoài base knowledge). Nhờ evaluation loop tự động, tôi hiểu rằng pipeline RAG thực chất là cấu nối giữa 2 bài toán hoàn toàn độc lập: Tìm kiếm (Search Engine - Retrieval) và Đọc & Trả lời (Reading Comprehension - Generation), không nên đổ lỗi sai sai vòng giữa chúng.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Khó khăn mất nhiều thời gian nhất của tôi là việc tự động hóa quá trình chạy `eval.py` để ra thẻ điểm scorecard mà không bị rate limit từ API của OpenAI khi gọi quá nhiều truy vấn judge cùng lúc. Giả thuyết ban đầu tôi cho rằng các metric sẽ dễ dàng đánh giá 1-5 chỉ bằng việc so string matching, nhưng thực tế với những câu hỏi phức tạp về phiên bản (như q10 về chính sách hoàn tiền version 4 áp dụng thế nào), judge đôi khi tự bị "confuse" nếu prompt cho chính judge không đưa các quy tắc chấm khắt khe.
Điều ngạc nhiên lớn là khả năng "Abstain" (Từ chối trả lời) cực kỳ khó cấu hình ở baseline. Rất nhiều lần model thà "bịa" ra cách tạo lỗi ERR-403 thay vì ngoan ngoãn nói "không xác định" dù đã có rule trong Grounded Prompt. Buộc nhóm phải sửa lại system prompt cứng rắn hơn rất nhiều.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** [q09] "ERR-403-AUTH là lỗi gì và cách xử lý?"

**Phân tích:** 
Câu này là một bài toán thử nghiệm khả năng **Abstain** (anti-hallucination) của hệ thống vì hoàn toàn không có đề cập về lỗi ERR-403-AUTH trong các file helpdesk. 
Đầu tiên, hệ thống Baseline (Dense Search) trả lời sai bằng cách đưa ra các gợi ý thay đổi mật khẩu thông thường. Điểm Faithfulness cho câu này tụt xuống mức rất thấp (~1/5) do lỗi Generation — LLM đã cố gắng "dịch" mã lỗi 403 thành lỗi xác thực chung chung và nhặt nhạnh các chunk không liên quan để tạo ảo giác.
Trong khi đó, ở hệ thống Variant, do chúng ta cấu hình Reranker với Cross-encoder kiểm tra khắt khe mức độ tương đồng giữa câu hỏi và đoạn trích, Reranking đã trả về những chunk thấp điểm (Loại đoạn văn). Do đó Context đưa vào Prompt trống hoặc không mang tính trả lời thông tin nào. Kết hợp với Prompt của Variant cứng rắn hơn, model đã trả lời đúng dự kiến: "Tôi không có đủ dữ liệu để trả lời". Qua đó, điểm Faithfulness và Relevance của câu hỏi này trong Variant Scorecard được tự động ghi nhận là 5/5. Đây là bằng chứng cho thấy giới hạn chunk bằng công nghệ Rerank kết hợp Abstain mang lại hiệu quả chống ảo giác RAG xuất sắc.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Nếu có thêm 1 giờ, tôi sẽ tích hợp và thử nghiệm công cụ **Ragas** (một thư viện đánh giá RAG chuyên nghiệp) thay cho những logic judge thủ công tĩnh tại. 
Nhìn vào kết quả scorecard, điểm Completeness thường lẹt đẹt mãi ở mức 3 hoặc 4 dù câu hỏi đơn giản. Nguyên do là LLM-judge có xu hướng chấm trừ điểm nếu trả lời có vẻ ngắn hơn Expected Answer. Do đó, tôi sẽ áp dụng tính năng Query Decomposition để chia nhỏ expected_answer ra nhiều ý, đánh tick chấm điểm từng thành phần ý để tính độ phủ thay vì so sánh gộp nội dung 1-5 như hiện tại.
