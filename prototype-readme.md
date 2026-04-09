# Prototype Readme — Trợ Lý AI Tài Xế Xanh SM

## Mô tả prototype

Chatbot hỗ trợ tài xế Xanh SM tra cứu chính sách và quy trình xử lý sự cố bằng ngôn ngữ tự nhiên tiếng Việt. Người dùng gõ câu hỏi → backend thực hiện Hybrid RAG (BM25 + FAISS + Cross-Encoder reranker) kết hợp LangGraph agent workflow → trả về câu trả lời kèm nguồn tài liệu, confidence badge, và cơ chế escalate tự động khi thông tin không đủ chắc chắn (đặc biệt với các con số tiền/mức phạt).

## Level: Working Prototype

Lý do phân loại Working Prototype (không phải Mock):

- Frontend Streamlit chạy live, nhận input và hiển thị response thật
- Backend FastAPI xử lý request, gọi AI thật qua OpenAI API
- Retrieval chạy thật trên knowledge base đã build từ tài liệu Xanh SM
- Agent workflow 4 node (classify → retrieve → answer → escalate) thực thi end-to-end
- Feedback loop cơ bản hoạt động qua endpoint `/feedback`

## Links

| Tài nguyên | Đường dẫn |
|---|---|
| Repo nhóm | `TODO — điền link GitHub public trước khi nộp` |
| Frontend entry point | `frontend/web_demo/app.py` |
| Backend entry point | `backend_ai/app/main_v3.py` |
| Agent workflow | `backend_ai/app/core/agent_graph_v4.py` |
| Retriever | `backend_ai/app/utils/retrieval_advanced.py` |
| SPEC final | `spec-final.md` |
| Eval script | `qa_eval/eval_scripts/eval_agent.py` |
| Eval dataset (ground truth) | `qa_eval/golden_datasets/testcases.json` |
| Video demo backup | `TODO — điền link Drive/YouTube trước khi nộp` |

## Tools và API đã dùng

**Backend:** Python · FastAPI · LangGraph · LangChain · OpenAI API (GPT-4o-mini)

**Retrieval:** FAISS (dense) · BM25Okapi (sparse) · Cross-Encoder reranker (`ms-marco-MiniLM-L-6-v2`) · SQLite chunk store · sentence-transformers

**Frontend:** Streamlit

**Data pipeline:** Python script · JSONL chunking · `setup_db.py` build FAISS + SQLite

## Kiến trúc prototype

```
[Streamlit] ──POST /chat──► [FastAPI]
                                │
                         [LangGraph Agent]
                         classify_node
                              │
                         retrieve_node
                         (BM25 + FAISS → RRF → CrossEncoder)
                              │
                         answer_node ──escalate?──► escalate_node
                              │
                    {reply, confidence, sources, escalate}
                                │
                         [Streamlit] hiển thị badge + nguồn
```

**Data flow đầy đủ:**

1. Tài liệu Xanh SM được crawl vào `data_pipeline/raw_data/`
2. Pipeline xử lý thành chunks → `setup_db.py` build `knowledge_base.sqlite` + `knowledge_base.faiss`
3. Frontend gửi `{message, thread_id}` tới `POST /chat`
4. Agent chạy 4 node: classify → retrieve → answer → (escalate nếu cần)
5. Frontend render câu trả lời + source tag + confidence badge + nút feedback

## Tính năng demo được

- Hỏi đáp chính sách bằng tiếng Việt tự nhiên
- Source citation — hiển thị tên tài liệu gốc dưới mỗi câu trả lời
- Confidence badge — màu xanh (high) / màu vàng "Cần xác nhận" (low)
- Escalate path — tự động chuyển sang gợi ý hotline khi có số tiền không chắc chắn hoặc không tìm được context
- Multi-turn memory — duy trì ngữ cảnh hội thoại qua `thread_id`
- Feedback endpoint — nút "Câu trả lời này không đúng" → `POST /feedback` → log error queue




# PHÂN CÔNG CÔNG VIỆC DỰ ÁN AI ASSISTANT XANH SM

## Nhiệm vụ từng thành viên

---

### 1. Đàm Lê Văn Toàn — Kỹ sư Dữ liệu (Data Engineer)

#### Vai trò:
Người xây nền móng dữ liệu cho toàn bộ hệ thống RAG.

#### Nhiệm vụ:
- Thu thập dữ liệu từ:
  - Website Xanh SM
  - Fanpage
  - File PDF chính sách
  - FAQ
  - Bảng giá dịch vụ
- Tiền xử lý dữ liệu:
  - Chuẩn hóa PDF/Excel sang Markdown hoặc JSON
  - Làm sạch dữ liệu lỗi, bỏ ký tự rác
- Chunking:
  - Chia tài liệu thành các đoạn nhỏ giữ nguyên ngữ cảnh
- Metadata tagging:
  - Gắn nhãn loại user: khách hàng / tài xế
  - Gắn loại dịch vụ: Xanh Bike / Xanh Car
- Embedding + lưu Vector DB:
  - Chuẩn bị dữ liệu cho ChromaDB / FAISS / Qdrant
- Tổng hợp failure modes liên quan dữ liệu thiếu / sai / mâu thuẫn

#### Output:
- `data_pipeline/raw_data/`
- `spec-final.md` phần Failure Modes

---

### 2. Hoàng Tuấn Anh — Kỹ sư Lõi AI & Backend (AI / Backend Engineer)

#### Vai trò:
Bộ não kỹ thuật của hệ thống.

#### Nhiệm vụ:
- Xây dựng Retrieval Pipeline:
  - Thiết kế `HybridRAGRetriever`
  - BM25 + FAISS + RRF fusion + CrossEncoder reranker
- Xây dựng agent workflow:
  - `agent_graph_v2`
  - `agent_graph_v3`
  - `agent_graph_v4`
  - Flow gồm 5 node:
    1. classify
    2. rephrase
    3. retrieve
    4. answer
    5. escalate
- Backend FastAPI:
  - `main_v1.py`
  - `main_v2.py`
  - `main_v3.py`
- Thiết kế response schema:
  - confidence
  - sources
  - escalate
  - query_type
- Prompt engineering:
  - Tách persona driver vs prospect
  - Prompt riêng cho answer node và escalate node
- Benchmark retrieval:
  - So sánh FAISS only vs Hybrid + Rerank
  - Test trên 3 truy vấn mẫu (utils/so_sanh_rag.md)


#### Output:
- `backend_ai/`
- integration modules

---

### 3. Phạm Tuấn Anh — Kỹ sư Giao diện & Tích hợp (Frontend Developer / Integrator)

#### Vai trò:
Phụ trách toàn bộ phần trải nghiệm người dùng.

#### Nhiệm vụ:
- Thiết kế Canvas UX flow
- Xây dựng giao diện demo:
  - Streamlit / Gradio chat interface
- Hiển thị kết quả:
  - Câu trả lời AI
  - Citation nguồn dữ liệu
  - Confidence score
  - Escalation notice khi cần chuyển người thật

- Giải quyết các lỗi CSS trong Streamlit để giao diện ổn định
- Tối ưu trải nghiệm demo pitching

#### Output:
- `spec-final.md` phần Canvas


---

## 4. Vũ Hồng Quang – Kỹ sư Kiểm thử 
Phụ trách QA và điều phối:



### Golden Dataset
- Xây dựng bộ test cases mẫu
- Chuẩn hóa file:
`qa_eval/golden_datasets/testcases.json`

### QA Testing
- Thiết kế câu hỏi thực tế từ:
  - khách hàng
  - tài xế
- Kiểm tra độ chính xác câu trả lời

### Demo Support
- Hỗ trợ chuẩn bị slide và demo pitching

### Hỗ trợ thiết kế eval metric
---

## 5. Nguyễn Quang Trường – Kỹ sư Kiểm thử & Đánh giá (QA / Evaluation Engineer)
Phụ trách đo lường chất lượng hệ thống:

- Thiết kế eval metrics:
  - Accuracy
  - Relevance
  - Faithfulness
  - Context Precision
- Hỗ trợ test/eval pipeline
- Red teaming:
  - kiểm tra câu hỏi đánh lừa
  - kiểm tra out-of-scope queries
- Phối hợp với backend để cải thiện retrieval quality

#### Output:
- `spec-final.md` phần Eval
- `qa_eval/`

---
### 6. Vũ Lê Hoàng — AI Prototype Developer (Version 1 Builder)

#### Vai trò:
Người phụ trách xây dựng phiên bản đầu tiên (V1) của hệ thống để tạo nền thử nghiệm ban đầu cho toàn team.

#### Nhiệm vụ:
- Xây dựng prototype V1 của chatbot AI assistant:
  - Tạo phiên bản chatbot chạy end-to-end đầu tiên
  - Kết nối thử nghiệm frontend ↔ backend ↔ retrieval pipeline
- Viết baseline retrieval flow:
  - Query user → search vector DB → trả context cho LLM
- Tạo bản prompt V1:
  - Prompt system cơ bản cho chatbot
  - Ép AI chỉ trả lời theo tài liệu truy xuất được
- Tích hợp thử nghiệm LLM API:
  - OpenAI / local model endpoint
- Test luồng hội thoại đầu tiên:
  - Kiểm tra bot trả lời đúng format
- Hỗ trợ Hoàng Tuấn Anh:
  - Làm nền tảng để nâng cấp lên Hybrid RAG Retriever

#### Output:
- Prototype chatbot V1 source code
- Baseline retrieval pipeline
- Initial prompt template V1
- Demo bản chạy thử đầu tiên của hệ thống

---

## Quy trình phối hợp

### Giai đoạn 1: Data Foundation
Toàn → hoàn thiện dữ liệu sạch và vector DB

### Giai đoạn 2: Core AI Development
Hoàng và Hoàng Tuấn Anh → xây retrieval + agent + backend

### Giai đoạn 3: UI Integration
Phạm Tuấn Anh → frontend demo + canvas flow

### Giai đoạn 4: QA & Evaluation
Trường + Quang + Vũ Lê Hoàng → test, metrics, golden dataset

### Giai đoạn 5: Final Integration
Cả team ráp hệ thống + chạy demo end-to-end

---
