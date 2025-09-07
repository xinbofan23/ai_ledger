import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from google.genai import types
from agent import adk_setup
import logging

load_dotenv(override=True)

app = FastAPI(debug=False)
logger = logging.getLogger("api")
logging.basicConfig(level=logging.INFO)

static_dir = Path(__file__).with_name("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Home page
@app.get("/")
async def index():
    return FileResponse(static_dir / "index.html")

# Initialize ADK runner at startup
@app.on_event("startup")
async def on_startup():
    try:
        runner = await adk_setup()
        app.state.runner = runner
        logger.info("[startup] runner ready: %s", type(runner).__name__)
    except Exception as e:
        app.state.runner = None
        logger.exception("[startup] adk_setup failed: %r", e)

# Request model
class ChatReq(BaseModel):
    message: str
    user_id: str | None = "user_1"
    session_id: str | None = "session_001"

# Send one message to the root agent and return the final text response
async def call_root_agent_once(runner, text: str, user_id: str, session_id: str) -> str:
    content = types.Content(role="user", parts=[types.Part(text=text)])
    final_text = None

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content,
    ):
        if hasattr(event, "is_final_response") and event.is_final_response():
            if getattr(event, "content", None) and getattr(event.content, "parts", None):
                parts = [getattr(p, "text", "") or "" for p in event.content.parts]
                final_text = "".join(parts).strip()
            if not final_text and hasattr(event, "text"): 
                final_text = (event.text or "").strip()

    return final_text or "(agent returned no text)"

# Chat endpoint
@app.post("/chat")
async def chat(req: ChatReq):
    runner = getattr(app.state, "runner", None)
    if runner is None:
        return JSONResponse({"error": "Runner not ready"}, status_code=503)
    try:
        reply = await call_root_agent_once(runner, req.message, req.user_id, req.session_id)
        return {"reply": reply}
    except Exception as e:
        logger.exception("Error in /chat: %r", e)
        return JSONResponse({"error": "Internal server error"}, status_code=500)

# Global exception handler
@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %r", exc)
    return JSONResponse({"error": "Internal server error"}, status_code=500)

# Health check
@app.get("/health")
async def health():
    ready = hasattr(app.state, "runner") and app.state.runner is not None
    return {"ok": True, "runner_ready": ready}

# Debug endpoint (enable only when DEBUG=1)
@app.get("/debug/runner")
async def debug_runner():
    if os.getenv("DEBUG") != "1":
        return JSONResponse({"error": "disabled"}, status_code=404)
    runner = getattr(app.state, "runner", None)
    return {"runner": str(type(runner)) if runner else None}
