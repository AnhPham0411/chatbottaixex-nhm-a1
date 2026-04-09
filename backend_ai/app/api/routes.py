from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from langchain_core.messages import ToolMessage
from app.core.agent_graph import app_graph
from app.core import config

router = APIRouter()

# Schema dữ liệu do Frontend gửi lên
class ChatRequest(BaseModel):
    prompt: str
    thread_id: str = Field(alias=config.USER_IDENTIFIER_KEY, default="default_user")

# Schema dữ liệu Backend trả về
class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []
    thread_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Cấu hình thread_id để LangGraph nhận diện và nhớ lịch sử khách hàng
        thread_config = {"configurable": {"thread_id": request.thread_id}}
        
        inputs = {"messages": [("human", request.prompt)]}
        
        # Chạy toàn bộ luồng Agent Graph
        final_state = app_graph.invoke(inputs, config=thread_config)
        
        # Lấy nội dung tin nhắn cuối cùng do AI sinh ra
        bot_response = final_state["messages"][-1].content
        
        # Trích xuất nguồn (sources) từ các ToolMessage trong history
        sources = []
        for msg in final_state["messages"]:
            if isinstance(msg, ToolMessage):
                # Giả định nội dung tool trả về có thể là list docs hoặc string
                # Ở đây ta lấy metadata nếu có, hoặc parse từ content
                # Dựa trên HybridRAGRetriever, metadata['source'] được dùng.
                # Tuy nhiên LangGraph ToolNode bọc kết quả tool vào content.
                # Nếu tool return List[Document], content sẽ là chuỗi đại diện.
                # Cách tốt nhất là truy cập artifacts nếu có, nhưng đơn giản nhất là trích xuất từ chính kết quả search.
                try:
                    # Kiểm tra xem có metadata source không (phụ thuộc vào cách tool được định nghĩa)
                    # Nếu tool trả về string, ta có thể tìm kiếm các pattern.
                    # Ở đây HybridRAGRetriever được bọc qua create_retriever_tool, 
                    # nó trả về string docs được nối lại.
                    pass
                except:
                    pass
        
        # Lưu ý: Vì Agent mang tính linh hoạt, ta sẽ tìm các thẻ nguồn nếu LLM có đề cập 
        # Hoặc lấy trực tiếp từ metadata của retriever nếu ta can thiệp sâu hơn.
        # Để đơn giản và chính xác, ta sẽ lấy unique section_titles từ kết quả search.
        
        unique_sources = []
        for msg in final_state["messages"]:
            if isinstance(msg, ToolMessage):
                # Tool search trả về nội dung có chứa section_title (metadata)
                # Trong HybridRAGRetriever, chúng ta gán metadata={"source": cand.section_title}
                # Khi ToolNode chạy, nó chuyển Document thành string.
                # Ta có thể lấy lại từ state nếu retriever gán vào metadata của message.
                if hasattr(msg, "artifact") and msg.artifact:
                    for doc in msg.artifact:
                        source = doc.metadata.get("source")
                        if source and source not in unique_sources:
                            unique_sources.append(source)
                elif "metadata" in msg.additional_kwargs:
                    # Một số wrapper khác
                    pass

        return ChatResponse(
            answer=bot_response,
            sources=unique_sources,
            thread_id=request.thread_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống AI: {str(e)}")