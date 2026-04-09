# SPEC Final — Trợ Lý AI Cho Tài Xế Xanh SM

**Track D — Xanh SM**

---

## Problem Statement

> Tài xế Xanh SM thường xuyên gặp vướng mắc về chính sách thưởng/phạt và cách xử lý sự cố với khách hàng, nhưng không có nơi tra cứu nhanh đáng tin cậy — họ phải hỏi đồng nghiệp (dễ sai), gọi tổng đài (chờ lâu), hoặc đọc tài liệu dài khó hiểu. Sản phẩm AI của nhóm hướng đến việc trả lời bằng ngôn ngữ tự nhiên từ tài liệu chính thức của Xanh SM, đồng thời biết khi nào cần chuyển sang hỗ trợ con người.

---

## 1. AI Product Canvas

|  | VALUE | TRUST | FEASIBILITY |
|---|---|---|---|
| **Nội dung** | **User:** Tài xế Xanh SM đang chạy ca (8–12h/ngày), không có thời gian đọc tài liệu dài. **Pain:** (1) Không biết chính sách thưởng/phạt mới nhất — hỏi đồng nghiệp thường nhận câu trả lời sai. (2) Gặp sự cố với khách (hủy chuyến sai, quên đồ, khiếu nại) → không biết quy trình báo cáo, sợ bị phạt oan. **AI giải quyết gì:** Tra cứu tức thì từ tài liệu chính thức bằng câu hỏi thường ngày. Cách hiện tại không làm được: tài liệu PDF không có search tốt, hotline chỉ phục vụ giờ hành chính. | **Khi AI sai:** Tài xế thực hiện sai quy trình → bị phạt tiền hoặc mất chuyến — thiệt hại tài chính trực tiếp. **User biết AI sai bằng cách nào:** Luôn hiển thị tên tài liệu gốc bên dưới câu trả lời. Nếu confidence thấp → hiện badge "Cần xác nhận" + nút gọi hotline. **User sửa bằng cách nào:** Nút "Câu trả lời này không đúng" → ghi nhận + escalate. **Trust recovery:** Luôn có nút "Gọi hỗ trợ ngay" ở mọi màn hình — tài xế không bao giờ bị bế tắc. | **Chi phí:** ~$0.003–0.008/query (GPT-4o-mini + embedding). 1.000 query/ngày ≈ $3–8/ngày. **Latency:** Pipeline ước tính 2–4 giây/query — chấp nhận được khi tài xế đỗ xe tra cứu. **Rủi ro chính:** (1) Tài liệu Xanh SM nội bộ — cần xin phép data. (2) Chính sách thay đổi thường xuyên → cần pipeline cập nhật định kỳ. (3) Tài xế dùng điện thoại cũ, mạng 3G yếu → phải tối ưu response nhỏ gọn. |

### Automation hay Augmentation?

**☑ Augmentation** — AI trả lời và trích dẫn nguồn, tài xế đọc và quyết định hành động.

**Lý do:** Nếu sai mà tài xế không biết (automation) → thực hiện sai quy trình → bị phạt tiền thật. Cost of error quá cao để tin tưởng hoàn toàn vào AI. Augmentation với nguồn trích dẫn cho phép tài xế tự verify trong vòng 5 giây.

---

### Learning Signal

| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | User correction đi vào đâu? | Nút "Không đúng" → log query + response + correction tag → weekly review bởi ops team Xanh SM |
| 2 | Product thu signal gì để biết tốt lên hay tệ đi? | (a) Implicit: tài xế có bấm "Xem tài liệu gốc" không — nếu hay bấm thì AI chưa trả lời đủ rõ. (b) Explicit: thumbs up/down sau mỗi câu trả lời. (c) Correction: câu nào bị báo sai → thêm vào eval test set. |
| 3 | Loại data | ☑ Domain-specific (chính sách Xanh SM) · ☑ Human-judgment (ops team verify) · ☑ Correction (tài xế báo sai) |

**Marginal value:** Tài liệu chính sách Xanh SM là data độc quyền — không model nào có sẵn. Mỗi correction từ tài xế là signal về edge case thực tế. Đây là data flywheel thực sự: càng nhiều tài xế dùng → càng nhiều correction → model ngày càng chính xác hơn với corpus riêng của Xanh SM.

---

## 2. User Stories × 4 Paths

**Persona:** Anh Minh, 34 tuổi, tài xế Xanh SM 2 năm, chạy ca sáng 6h–14h. Dùng Android đời 2021, hay dùng điện thoại khi đỗ xe chờ khách.

---

### Path 1 — Happy Path: AI trả lời đúng

> **Trigger:** Anh Minh nhận được thông báo bị trừ 50k, không hiểu tại sao.

**Hành động:** Mở app → gõ "tại sao tôi bị trừ tiền hôm qua?"

**Hệ thống làm gì:**
- Classify query → retrieve đúng mục "Chính sách khấu trừ" + "Lỗi vi phạm"
- Trả lời: "Theo chính sách tháng 4/2026, tài xế bị trừ 50k nếu hủy chuyến sau khi đã nhận — áp dụng từ lần thứ 3 trong tháng."
- Hiển thị tên tài liệu gốc + confidence badge xanh

**Anh Minh thấy gì:** Câu trả lời rõ ràng + nguồn → hiểu ngay, không cần hành động thêm.

**Value moment:** Tiết kiệm 10 phút gọi tổng đài, có câu trả lời chính xác ngay trên xe.

---

### Path 2 — Low Confidence Path: AI không chắc

> **Trigger:** Anh Minh gặp tình huống lạ — khách đặt xe rồi nhờ đổi điểm đến sang tỉnh khác giữa chừng.

**Hành động:** Gõ "khách muốn đổi từ Hà Nội đi Hải Phòng được không, tôi xử lý thế nào?"

**Hệ thống làm gì:**
- Retrieve — không tìm thấy policy rõ ràng cho trường hợp liên tỉnh
- **Không đoán bừa.** Trả lời: "Tôi tìm thấy quy định về đổi điểm đến trong nội thành, nhưng chưa có thông tin rõ ràng về chuyến liên tỉnh."
- Hiển thị badge màu vàng "Cần xác nhận" + nút [Gọi hỗ trợ ngay — 1900xxxx]

**Anh Minh thấy gì:** AI thành thật về giới hạn của mình → tài xế không hành động sai vì tin nhầm.

**Design principle:** Badge màu vàng — không dùng màu đỏ (không phải lỗi hệ thống) cũng không dùng màu xanh (không phải chắc chắn).

---

### Path 3 — Failure Path: AI trả lời sai

> **Trigger:** AI trả lời nhầm mức thưởng cuối tuần do dùng tài liệu cũ tháng 3 thay vì tháng 4.

**Anh Minh phát hiện:** Làm theo hướng dẫn nhưng không nhận được thưởng như AI nói → nghi ngờ.

**Recovery flow (tối đa 2 bước):**
1. Bấm "Câu trả lời này không đúng" ngay dưới message
2. Chọn lý do nhanh: [Thông tin cũ] [Không áp dụng cho trường hợp của tôi] [Khác] → App ghi nhận + gợi ý "Bạn muốn gọi hỗ trợ để xác nhận không?"

**Hệ thống làm gì sau đó:**
- Log query vào error queue
- Ops team review trong vòng 24h
- Nếu xác nhận tài liệu cũ → cập nhật knowledge base + tag tất cả query tương tự là "Cần verify"

**Thiệt hại giới hạn:** Tài xế mất 5 phút gọi hotline xác nhận — không mất tiền thật vì đây là augmentation, tài xế vẫn check trước khi hành động.

---

### Path 4 — Recovery Path: Tài xế mất niềm tin

> **Trigger:** Sau 2 lần nhận thông tin sai về chính sách, anh Minh không tin app nữa.

**Lối thoát rõ ràng:**
- Nút "Hotline hỗ trợ" luôn hiện — không bị ẩn sau menu
- Khi tài xế bấm "Không đúng" lần thứ 2 trong session → app tự động hỏi "Bạn có muốn nói chuyện trực tiếp với nhân viên hỗ trợ không?"

**Transparency:**
- Mỗi câu trả lời hiển thị: "Nguồn: [Tên tài liệu] · Cập nhật: [ngày]"
- Tài xế biết AI dựa vào tài liệu gì → tự đánh giá độ tin cậy

**Opt-out:**
- Trong Settings: "Tắt gợi ý AI, chỉ hiển thị tài liệu gốc" → app trở thành search engine đơn giản, không qua LLM

---

## 3. Eval Metrics

### 3 chỉ số chính

| # | Metric | Đo bằng cách nào | Threshold "đủ tốt" | Red flag |
|---|---|---|---|---|
| 1 | **Retrieval Accuracy** — AI tìm đúng tài liệu liên quan không? | Ground truth: 100 câu hỏi mẫu do nhóm viết, check top-3 chunks có chứa câu trả lời đúng không | ≥ 85% | < 70%: knowledge base cần restructure |
| 2 | **Answer Faithfulness** — AI có bịa thông tin ngoài tài liệu không? | Human eval: 50 câu trả lời ngẫu nhiên/tuần, check từng claim có trong source doc không | ≥ 95% — zero tolerance với hallucination về số tiền/mức phạt | < 90%: tắt tính năng, review prompt |
| 3 | **Escalation Precision** — Khi AI nói "Cần xác nhận", có đúng là cần xác nhận không? | Nhóm verify 20 câu "Cần xác nhận"/tuần, đối chiếu với tài liệu | ≥ 80% | < 60%: AI đang over-hedge, mất tín nhiệm |

### Precision vs Recall — lựa chọn

**Ưu tiên Precision cao hơn** cho metric số 2 (faithfulness): tài xế bị phạt oan vì làm theo thông tin sai = thiệt hại tài chính thật. Bỏ sót 1 trường hợp (nói "không biết" khi thực ra biết) chỉ khiến tài xế mất thêm 5 phút gọi hotline — chấp nhận được.

**Recall quan trọng hơn** cho metric số 1 (retrieval) — bỏ sót tài liệu liên quan còn nguy hiểm hơn retrieve thừa.

### Eval iteration plan

```
Bước 1: Chạy 100 câu hỏi mẫu thủ công → ghi nhận lỗi nào nhiều nhất
Bước 2: Sửa chunking strategy / prompt → chạy lại → so sánh delta
Bước 3: Automation — log production queries → weekly human spot-check 50 câu
```

Dataset hiện tại: `qa_eval/golden_datasets/testcases.json`
Script eval: `qa_eval/eval_scripts/eval_agent.py`

---

## 4. Top 3 Failure Modes

### Failure Mode 1 — Tài liệu cũ: AI trả lời theo chính sách đã hết hạn

| | Chi tiết |
|---|---|
| **Trigger** | Xanh SM cập nhật chính sách thưởng/phạt nhưng knowledge base chưa được sync |
| **Hậu quả** | Tài xế làm theo thông tin cũ → không nhận được thưởng hoặc bị phạt oan → khiếu nại Xanh SM, mất niềm tin vào app |
| **Mitigation** | (1) Mỗi chunk trong knowledge base có trường `updated_at`. (2) AI hiển thị "Tài liệu ngày X" — tài xế tự đánh giá. (3) Khi tài liệu > 30 ngày không được cập nhật → auto-badge "Có thể đã hết hạn". (4) Pipeline sync tài liệu mới mỗi 7 ngày. |
| **Hiện trạng** | Timestamp chunk đã có trong schema SQLite — UI chưa render, đưa vào Sprint 1 |

---

### Failure Mode 2 — Hallucination về con số cụ thể (mức thưởng, mức phạt)

| | Chi tiết |
|---|---|
| **Trigger** | Query hỏi về số tiền cụ thể ("thưởng chuyến VIP là bao nhiêu?") mà tài liệu không có con số rõ ràng → AI suy diễn |
| **Hậu quả** | Nghiêm trọng nhất — tài xế tin vào con số sai, hoặc claim Xanh SM nợ tiền dựa trên thông tin AI bịa. Rủi ro pháp lý cho Xanh SM. |
| **Mitigation** | (1) System prompt cấm suy đoán số tiền khi không có trong tài liệu. (2) `answer_node`: nếu `has_money_figure=True` và `confidence≠high` → route sang `escalate_node`. (3) Post-processing regex detect pattern VNĐ trong response — nếu không có citation chunk đi kèm → override sang escalate. (4) Eval weekly: 100% câu trả lời có số tiền đều được human check. |
| **Hiện trạng** | Lớp (2) đã implement. Lớp (3) post-processing regex chưa có — đưa vào Sprint 1 vì đây là safety gap. |

---

### Failure Mode 3 — Misclassify sự cố: AI hướng dẫn sai quy trình xử lý

| | Chi tiết |
|---|---|
| **Trigger** | Tài xế mô tả sự cố mơ hồ ("khách không chịu xuống xe") → AI classify nhầm loại incident → retrieve sai SOP → hướng dẫn sai bước xử lý |
| **Hậu quả** | Tài xế không thu thập đúng bằng chứng / báo cáo sai kênh → khi khiếu nại xảy ra, tài xế không có đủ căn cứ để bảo vệ mình |
| **Mitigation** | (1) Với query về sự cố: `classify_node` detect `needs_clarification=True` → hỏi lại 1 câu trước khi retrieve. (2) Khi không chắc chắn về loại sự cố → hiện top 2 SOP khả năng nhất để tài xế chọn. (3) Luôn kèm: "Nếu sự cố nghiêm trọng, gọi ngay hotline 1900xxxx." |
| **Hiện trạng** | `needs_clarification` đã implement ở `classify_node`. UI render top-2 SOP chưa có — đưa vào Sprint 2. |

---

## 5. ROI — 3 Kịch bản

### Baseline (hiện tại, không có AI)

- Hotline nhận ~500 cuộc/ngày từ tài xế hỏi chính sách/sự cố
- 1 nhân viên hỗ trợ xử lý ~80 cuộc/ngày → cần 6–7 nhân viên cho mảng này
- Chi phí nhân sự: ~6 người × 8 triệu/tháng = **48 triệu/tháng**
- Tài xế: chờ trung bình 8 phút/cuộc → mất ~67 giờ tài xế/ngày

### Chi phí vận hành AI (ước tính)

- Infrastructure: ~$50/tháng (vector DB + hosting)
- API cost: ~$150/tháng (50k queries × $0.003)
- Maintenance: 0.5 FTE ops (~4 triệu/tháng)
- **Tổng: ~5.5 triệu/tháng**

---

| | Conservative | Realistic | Optimistic |
|---|---|---|---|
| **Giả định** | AI xử lý 30% queries, adoption 20% tài xế | AI xử lý 60% queries, adoption 50% tài xế | AI xử lý 80% queries, adoption 80% tài xế, data flywheel hoạt động |
| **Hotline giảm** | 15% (~75 cuộc/ngày) | 35% (~175 cuộc/ngày) | 55% (~275 cuộc/ngày) |
| **Nhân sự tiết kiệm** | 1 FTE (~8 triệu/tháng) | 2–3 FTE (~20 triệu/tháng) | 4 FTE (~32 triệu/tháng) |
| **Giá trị tài xế** (thời gian tiết kiệm) | 10 giờ/ngày × 200k/giờ ≈ 60 triệu/tháng | 30 giờ/ngày ≈ 180 triệu/tháng | 55 giờ/ngày ≈ 330 triệu/tháng |
| **Chi phí AI** | 5.5 triệu/tháng | 5.5 triệu/tháng | 5.5 triệu/tháng |
| **Net benefit** | ~62.5 triệu/tháng | ~194.5 triệu/tháng | ~356.5 triệu/tháng |
| **ROI** | 11x | 35x | 65x |

### Kill criteria

Dừng hoặc pivot khi:
- Answer Faithfulness < 90% trong 2 tuần liên tiếp (rủi ro pháp lý)
- Tỷ lệ tài xế báo sai > 15% tổng queries
- Chi phí API vượt 30% giá trị tiết kiệm hotline thu được

---

## 6. Mini AI Spec

```
════════════════════════════════════════════════════════
TRỢ LÝ AI CHO TÀI XẾ XANH SM — Mini Spec
════════════════════════════════════════════════════════

VẤN ĐỀ
  Tài xế Xanh SM không có nơi tra cứu nhanh chính sách
  và quy trình sự cố — hotline chờ lâu, tài liệu khó đọc,
  hỏi đồng nghiệp hay sai.

GIẢI PHÁP
  RAG chatbot: tài xế hỏi bằng tiếng Việt thường ngày
  → AI tìm trong tài liệu chính thức → trả lời + trích nguồn.
  Khi không chắc → nói thẳng + đưa hotline.

NGƯỜI DÙNG
  Tài xế Xanh SM đang chạy ca, dùng điện thoại Android.

LOẠI AI
  Augmentation (AI gợi ý, tài xế quyết định hành động).
  Không automation — cost of error quá cao.

STACK
  LangGraph (4 node: classify → retrieve → answer → escalate)
  + FAISS (dense) + BM25 (sparse) + RRF + Cross-Encoder reranker
  + SQLite chunk store + GPT-4o-mini + Streamlit

DATA SOURCE
  Tài liệu nội bộ Xanh SM: chính sách thưởng/phạt,
  SOP sự cố, hợp đồng tài xế, FAQ.
  Đã crawl và build knowledge base.

SUCCESS METRICS
  - Retrieval Accuracy ≥ 85%
  - Answer Faithfulness ≥ 95% (zero hallucination về số tiền)
  - Escalation Precision ≥ 80%

TOP RISK
  Tài liệu cũ → hiển thị timestamp + sync 7 ngày/lần.
  Hallucination số tiền → post-process filter + human eval.
  Misclassify sự cố → hỏi lại 1 câu trước khi retrieve.

4 PATHS
  Happy:      Trả lời + hiện nguồn + badge xanh
  Low-conf:   Badge vàng "Cần xác nhận" + gợi ý hotline
  Failure:    Nút báo sai 1 bấm → ops team review 24h
  Recovery:   Hotline luôn hiện + option tắt AI hoàn toàn

ROI (Realistic)
  Tiết kiệm 2–3 FTE hotline + 30h tài xế/ngày
  ≈ 194.5 triệu/tháng net benefit vs 5.5 triệu chi phí = 35x ROI

LEARNING SIGNAL
  Implicit:   click "Xem tài liệu gốc" → AI chưa đủ rõ
  Explicit:   thumbs up/down sau mỗi câu trả lời
  Correction: nút "Không đúng" → error queue → weekly review

════════════════════════════════════════════════════════
```

---

## 7. Phân công

| Thành viên | Phần đảm nhận | Output |
|---|---|---|
| Hoàng Tuấn Anh | Canvas + User Stories 4 paths | `spec-final.md` phần 1, 2 |
| Vũ Lê Hoàng | Mini AI Spec + mô tả kiến trúc workflow | `spec-final.md` phần 6, mô tả agent pipeline |
| Nguyễn Quang Trường | test/eval support + hỗ trợ demo | `spec-final.md` phần 3, `qa_eval/` |
| Đàm Lê Văn Toàn | Failure modes + tài liệu chính sách Xanh SM | `spec-final.md` phần 4, `data_pipeline/raw_data/` |
| Phạm Tuấn Anh | ROI + Prototype  | `spec-final.md` phần 5 |
| Vũ Hồng Quang | Eval metrics + Test cases mẫu  | `qa_eval/golden_datasets/testcases.json`, demo support |