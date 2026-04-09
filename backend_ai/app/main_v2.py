"""
main.py
Đặt tại: backend_ai/app/main.py
"""

from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from typing import List

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# LIFESPAN — load graph khi startup
# ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Import app_graph ở đây (không import ở top-level) để tránh
    FAISS + CrossEncoder load ngay lúc import module trong test.
    Chỉ load khi FastAPI thực sự khởi động.
    """
    logger.info("Loading RAG agent...")
    from app.core.agent_graph_v2 import app_graph  # noqa: F401 — trigger build
    logger.info("RAG agent ready.")
    yield


app = FastAPI(title="Chatbot Tài Xế Xanh SM API", lifespan=lifespan)


# ──────────────────────────────────────────────
# SCHEMA
# ──────────────────────────────────────────────

class ChatQuery(BaseModel):
    message: str
    thread_id: str = ""          # để trống → tự sinh UUID (stateless per request)

class ChatResponse(BaseModel):
    reply: str
    sources: List[str] = []
    thread_id: str = ""


# ──────────────────────────────────────────────
# ENDPOINTS
# ──────────────────────────────────────────────

@app.get("/")
async def root():
    return {"message": "Chatbot Tài Xế Xanh SM API — RAG enabled"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(query: ChatQuery):
    if not query.message.strip():
        raise HTTPException(status_code=400, detail="message không được để trống.")

    # thread_id để MemorySaver phân biệt các cuộc hội thoại
    # Frontend truyền thread_id cố định → agent nhớ lịch sử hội thoại
    # Frontend không truyền → mỗi request là 1 session mới
    thread_id = query.thread_id or str(uuid.uuid4())

    try:
        from app.core.agent_graph_v2 import app_graph

        result = app_graph.invoke(
            {"messages": [HumanMessage(content=query.message)]},
            config={"configurable": {"thread_id": thread_id}},
        )

        reply = result["messages"][-1].content

        # Thu thập sources từ ToolMessage
        import re
        sources: list[str] = []
        for msg in result["messages"]:
            if hasattr(msg, "name") and msg.name == "policy_search":
                found = re.findall(r"source='([^']+)'", getattr(msg, "content", ""))
                sources.extend(found)

        # Dedup giữ thứ tự
        seen: set[str] = set()
        unique_sources = [s for s in sources if not (s in seen or seen.add(s))]

        return ChatResponse(reply=reply, sources=unique_sources, thread_id=thread_id)

    except Exception as e:
        logger.error("Agent error: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Lỗi xử lý câu hỏi.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main_v2:app", host="0.0.0.0", port=8000, reload=True)