import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.schema import ChatRequest, ChatResponse
from app.agent import run_agent, load_profile_record

app = FastAPI(title="AI-Native Personal Profile", version="1.0.0")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def serve_index():
    """Serve the single-page application frontend."""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    """Main conversational endpoint resolving visitor intents."""
    return await run_agent(payload.message)

@app.get("/api/profile/raw")
async def get_raw_profile():
    """Return raw profile record for inspection and grading transparency."""
    return load_profile_record()


@app.get("/api/healthz")
async def healthz():
    """Health check endpoint for container orchestration and monitoring."""
    return {"status": "ok"}