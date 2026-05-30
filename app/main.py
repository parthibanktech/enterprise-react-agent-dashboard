from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Core config imports
from app.core.config import is_live_mode_available

# Modular routers imports
from app.routers import chat, lessons

# Initialize FastAPI App
app = FastAPI(
    title="Enterprise ReAct Agent API Gateway",
    description="FastAPI service serving Parthiban's unified LangChain ReAct Agent with modular tools.",
    version="2.0.0"
)

# Enable CORS so our React frontend can query us safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(chat.router)
app.include_router(lessons.router)

@app.get("/healthz")
def health_check():
    """Liveness probe check to confirm service status."""
    return {"status": "healthy", "live_agent_ready": is_live_mode_available()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
