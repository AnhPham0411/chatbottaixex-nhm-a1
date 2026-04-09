# Chatbot Tài Xế Xanh SM (NHM-A1)

Dự án chatbot hỗ trợ tài xế Xanh SM, sử dụng công nghệ RAG (Retrieval-Augmented Generation).

## Cấu trúc Dự án

Dự án được chia thành 4 phần chính tương ứng với 4 vai trò trong team:

### 1. Data Pipeline (`data_pipeline/`) - Data Engineer
- **scrapers/**: Thu thập dữ liệu từ Fanpage, Website Xanh SM.
- **raw_data/**: Chứa dữ liệu thô (PDF, Excel...).
- **processed_data/**: Dữ liệu đã chuẩn hóa sang Markdown/JSON.
- **db_setup/**: Đẩy dữ liệu vào Vector Database.

### 2. Backend AI (`backend_ai/`) - AI/Backend Engineer
- **app/**: API (FastAPI) và logic xử lý RAG.
- **core/**: Retrieval, LLM integration.
- **prompts/**: Quản lý System Prompts.

### 3. Frontend (`frontend/`) - Frontend / Integrator
- **web_demo/**: Giao diện Chat (Streamlit/React).
- **integrations/**: Kết nối Zalo OA, Messenger.

### 4. QA & Evaluation (`qa_eval/`) - QA / PM
- **golden_datasets/**: Bộ câu hỏi và trả lời chuẩn.
- **eval_scripts/**: Chấm điểm tự động (RAGAS).

## Hướng dẫn Setup nhanh
1. Clone dự án.
2. Sao chép `.env.example` thành `.env` và điền API Key.
3. Chạy `docker-compose up` (sau khi hoàn thiện Dockerfiles).

## Tài liệu
Xem chi tiết tại thư mục `docs/`.


streamlit run web_demo/app.py
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload