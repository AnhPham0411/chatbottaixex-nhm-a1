from fastapi import FastAPI
from app.api.routes import router as api_router

app = FastAPI(title="Chatbot Tài Xế Xanh SM API")

# Mount các tuyến đường API thực tế từ routes.py
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Chatbot Tài Xế Xanh SM API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
