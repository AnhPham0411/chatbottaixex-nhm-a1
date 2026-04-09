# Chatbot Tài Xế Xanh SM

Tài liệu gốc cho dev trong team để setup, chạy và nâng cấp trợ lý AI cho tài xế Xanh SM.

Kiến trúc hiện tại:

`data_pipeline -> SQLite/FAISS -> Hybrid Retrieval -> LangGraph Agent v4 -> FastAPI -> Streamlit`

README này bám theo runtime đang dùng trong repo:

- Backend API: `backend_ai/app/main_v3.py`
- Agent graph: `backend_ai/app/core/agent_graph_v4.py`
- Prompt chính: `backend_ai/app/prompts/system_prompt_v4.py`

## 1. Mục tiêu dự án

Hệ thống hỗ trợ tài xế Xanh SM theo mô hình RAG:

- Tra cứu nhanh chính sách, điều khoản và quy trình xử lý sự cố.
- Trả lời dựa trên tài liệu nội bộ đã được chunk và lập chỉ mục.
- Có cơ chế nhận biết câu hỏi mơ hồ, cần làm rõ hoặc cần chuyển sang hỗ trợ con người.
- Có `confidence`, `escalate`, `sources` và `feedback` để kiểm soát rủi ro.

## 2. Kiến trúc tổng quan

Luồng chính của hệ thống:

1. Thu thập và xử lý tài liệu trong `data_pipeline/`.
2. Build knowledge base cục bộ dạng `SQLite + FAISS`.
3. Backend nhận câu hỏi qua FastAPI.
4. LangGraph agent v4 chạy tuần tự:
   - `classify`
   - `rephrase`
   - `retrieve`
   - `answer`
   - `escalate`
5. Frontend Streamlit hiển thị câu trả lời, nguồn tham khảo và trạng thái tin cậy.

## 3. Cấu trúc thư mục quan trọng

### Data pipeline

- `data_pipeline/scrapers/test_crawl.py`
  - Crawl nội dung policy từ website Xanh SM và lưu về `data_pipeline/raw_data/`.
- `data_pipeline/processed_data/`
  - Nơi chứa dữ liệu đã chuẩn hóa, đặc biệt là `chunks.jsonl`.
- `data_pipeline/db_setup/setup_db.py`
  - Build `knowledge_base.sqlite` và `knowledge_base.faiss`.
  - Sinh embedding bằng `sentence-transformers`.

### Backend AI

- `backend_ai/app/main.py`
  - API cũ, chỉ nên giữ để tham khảo.
- `backend_ai/app/main_v2.py`
  - Bản trung gian với graph tool-calling và memory theo `thread_id`.
- `backend_ai/app/main_v3.py`
  - Entry point API hiện tại.
  - Trả về `reply`, `confidence`, `query_type`, `escalate`, `sources`, `thread_id`.
  - Có endpoint `POST /feedback`.
- `backend_ai/app/core/agent_graph_v3.py`
  - Bản agent v3, đã tách các node cơ bản.
- `backend_ai/app/core/agent_graph_v4.py`
  - Bản agent mới nhất đang dùng.
  - Graph hiện tại:
    - `classify -> rephrase -> retrieve -> answer -> escalate`
  - Có thêm:
    - phân loại `driver` / `prospect`
    - phân loại `policy` / `incident` / `recruitment` / `general`
    - rewrite câu hỏi theo lịch sử hội thoại
    - memory theo `thread_id`
- `backend_ai/app/prompts/system_prompt.py`
  - Prompt cũ của các bản đầu.
- `backend_ai/app/prompts/system_prompt_v3.py`
  - Prompt cho agent v3.
- `backend_ai/app/prompts/system_prompt_v4.py`
  - Prompt mới nhất cho v4:
    - `CLASSIFY_PROMPT`
    - `REPHRASE_PROMPT`
    - `ANSWER_DRIVER_PROMPT`
    - `ANSWER_PROSPECT_PROMPT`
    - `ESCALATE_DRIVER_PROMPT`
    - `ESCALATE_PROSPECT_PROMPT`
- `backend_ai/app/utils/retrieval_advanced.py`
  - Hybrid retrieval:
    - FAISS dense search
    - BM25 sparse search
    - Reciprocal Rank Fusion
    - Cross-encoder reranker
- `backend_ai/app/core/config.py`
  - Cấu hình đường dẫn DB/FAISS, model embedding và model LLM.

### Frontend

- `frontend/web_demo/app.py`
  - Streamlit chat UI.
  - Gọi `POST /chat` đến backend.
  - Giữ `thread_id` trong session để agent nhớ hội thoại theo phiên.

### Tài liệu và đánh giá

- `spec.md`
  - SPEC draft / logic sản phẩm AI.
- `spec-final.md`
  - Phiên bản hoàn thiện của spec nếu team đã chốt.
- `plan_hackathon.md`
  - Kế hoạch triển khai và tiến độ hackathon.
- `reflection.md`
  - Tổng kết, bài học, điểm đã làm được và chưa làm được.
- `prototype-readme.md`
  - Tài liệu phục vụ demo prototype.
- `qa_eval/`
  - Thư mục dành cho evaluation và test cases.

## 4. Agent graph v4 hoạt động như thế nào

### Bước 1: `classify`

Node `classify` xác định:

- `user_persona`: `driver` hay `prospect`
- `query_type`: `policy`, `incident`, `recruitment`, `general`
- `needs_clarification`: có cần hỏi làm rõ hay không

Mục tiêu:

- Tách câu hỏi của tài xế đang chạy xe với người đang tìm hiểu để đăng ký.
- Tránh dùng chung một prompt cho hai tình huống rất khác nhau.
- Nếu câu hỏi quá mơ hồ, hệ thống dừng sớm để hỏi lại thay vì trả lời đoán.

### Bước 2: `rephrase`

Node `rephrase` viết lại câu hỏi mới nhất thành một `search_query` độc lập, đầy đủ ngữ cảnh.

Ví dụ:

- User turn 1: “Điều khoản bao gồm những gì?”
- User turn 2: “Cái bạn vừa nói ý”

Thì `rephrase` có nhiệm vụ biến câu thứ hai thành một truy vấn rõ nghĩa hơn để retrieval tìm đúng tài liệu.

### Bước 3: `retrieve`

Node `retrieve` dùng `search_query` để truy xuất tài liệu bằng `HybridRAGRetriever`.

Retriever hiện tại gồm:

- Dense search bằng FAISS
- Sparse search bằng BM25
- Hợp nhất kết quả bằng RRF
- Chấm lại bằng Cross-encoder reranker

Mục tiêu:

- Dense search bắt được ý nghĩa gần đúng.
- BM25 bắt được từ khóa policy chính xác.
- Reranker chọn lại top chunk liên quan nhất để giảm nhiễu.

### Bước 4: `answer`

Node `answer` chọn prompt theo `user_persona`:

- `driver` dùng prompt tra cứu chính sách
- `prospect` dùng prompt tư vấn, mềm hơn và có CTA

Node này trả về:

- `answer`
- `confidence`
- `has_money_figure`
- `escalate`

Logic hiện tại:

- Nếu không có context: `escalate = True`
- Nếu có số tiền nhưng độ tin cậy thấp: `escalate = True`
- Nếu độ tin cậy thấp nhưng vẫn có thông tin hữu ích: vẫn trả lời, giữ `confidence = low`

### Bước 5: `escalate`

Node `escalate` chỉ chạy khi:

- không tìm được context
- hoặc có câu trả lời chứa thông tin nhạy cảm nhưng chưa đủ chắc chắn

Node này tạo câu trả lời an toàn hơn và hướng người dùng sang hotline / hỗ trợ con người.

## 5. Setup môi trường

### Yêu cầu

- Python 3.11+ khuyến nghị
- Có `pip`
- Có `OPENAI_API_KEY`

### Tạo virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Cài dependencies

Backend:

```powershell
pip install -r backend_ai/requirements.txt
```

Data pipeline:

```powershell
pip install -r data_pipeline/requirements.txt
```

### Tạo file môi trường

Repo hiện đang dùng file `.env`.

Ví dụ tối thiểu:

```env
OPENAI_API_KEY=your_openai_api_key_here
BACKEND_URL=http://localhost:8000/chat
```

Lưu ý:

- README cũ từng nhắc `.env.example`, nhưng hiện tại repo không còn file này.
- Cấu hình lõi của backend vẫn nằm trong `backend_ai/app/core/config.py`.

## 6. Build knowledge base

Mặc định `setup_db.py` đọc từ:

- `data_pipeline/processed_data/chunks.jsonl`

Và sinh ra:

- `data_pipeline/db_setup/knowledge_base.sqlite`
- `data_pipeline/db_setup/knowledge_base.faiss`

Lệnh chạy:

```powershell
python data_pipeline/db_setup/setup_db.py
```

Hoặc truyền tham số rõ ràng:

```powershell
python data_pipeline/db_setup/setup_db.py --chunks-file data_pipeline/processed_data/chunks.jsonl --sqlite-path data_pipeline/db_setup/knowledge_base.sqlite --faiss-path data_pipeline/db_setup/knowledge_base.faiss
```

## 7. Chạy hệ thống

### Chạy backend FastAPI

Lệnh đang dùng:

```powershell
python backend_ai/app/main_v3.py
```

Hoặc chạy bằng `uvicorn` trong thư mục `backend_ai`:

```powershell
cd backend_ai
uvicorn app.main_v3:app --host 0.0.0.0 --port 8000 --reload
```

### Chạy frontend Streamlit

```powershell
streamlit run frontend/web_demo/app.py
```

Frontend hiện gọi:

- `POST http://localhost:8000/chat`

## 8. API tham chiếu

### `POST /chat`

Request:

```json
{
  "message": "string",
  "thread_id": "string"
}
```

`thread_id` có thể để trống. Nếu để trống, backend sẽ tự sinh UUID mới.

Response:

```json
{
  "reply": "string",
  "confidence": "high",
  "query_type": "policy",
  "escalate": false,
  "sources": [
    {
      "title": "string",
      "url": "string",
      "chunk_id": 123,
      "rerank_score": 0.91
    }
  ],
  "thread_id": "string"
}
```

Ý nghĩa field:

- `confidence`: độ tin cậy của câu trả lời
- `query_type`: loại câu hỏi sau khi classify
- `escalate`: có cần chuyển sang hỗ trợ người thật hay không
- `sources`: metadata của các chunk được retrieve
- `thread_id`: định danh phiên hội thoại để giữ lịch sử

### `POST /feedback`

Request:

```json
{
  "thread_id": "string",
  "message_index": 0,
  "reason": "wrong_case",
  "detail": "string"
}
```

Response:

```json
{
  "status": "received",
  "message": "Cảm ơn phản hồi của bạn. Chúng tôi sẽ xem xét trong 24h."
}
```

## 9. Trạng thái hiện tại / Known gaps

Những điểm đã khớp runtime hiện tại:

- `main_v3.py` đang import `agent_graph_v4`
- `agent_graph_v4.py` đang dùng prompt `system_prompt_v4`
- `agent_graph_v4.py` đã có node `rephrase`

Những điểm còn lệch hoặc cần dọn tiếp:

- Trong block `if __name__ == "__main__"` của `backend_ai/app/main_v3.py`, lệnh `uvicorn.run(...)` vẫn đang trỏ tới `app.main:app`, chưa đổi sang `app.main_v3:app`.
- Frontend chưa phản ánh đầy đủ tất cả trạng thái backend trả về nếu team muốn demo trọn vẹn `confidence`, `escalate` và `feedback loop`.
- Tài liệu trong `docs/` chưa được cập nhật đồng bộ theo agent v4.

## 10. Version notes

- `v1`
  - Skeleton API, trả lời dummy.
- `v2`
  - Tool-calling graph có `thread_id` memory.
- `v3`
  - Tách node `classify -> retrieve -> answer -> escalate`.
- `v4`
  - Thêm `driver` / `prospect`
  - Thêm `rephrase` để xử lý follow-up theo lịch sử
  - Bổ sung `url` trong `sources`
  - Điều chỉnh logic `escalate` để an toàn hơn

## 11. Nên đọc file nào đầu tiên

Nếu tiếp tục nâng cấp hệ thống, nên đọc theo thứ tự:

1. `backend_ai/app/main_v3.py`
2. `backend_ai/app/core/agent_graph_v4.py`
3. `backend_ai/app/prompts/system_prompt_v4.py`
4. `backend_ai/app/utils/retrieval_advanced.py`
5. `frontend/web_demo/app.py`
6. `data_pipeline/db_setup/setup_db.py`
