from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic  import BaseModel, Field
from collections import deque, defaultdict
from typing import List, Dict, Any, Deque, Optional
import uuid
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from groq import Groq
import logging

# Load environment variables from a .env file (if it exists)
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Amit Pal's Portfolio API")

# Add CORS middleware for cross-domain requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log the body behind every 422 instead of silently returning one.
@app.exception_handler(RequestValidationError)
async def log_validation_error(request: Request, exc: RequestValidationError):
    body = (await request.body()).decode("utf-8", "replace")
    if len(body) > 300:                      # keep an oversized payload from flooding the log
        body = body[:300] + f"... [{len(body)} chars total]"
    logger.error("422 on %s | body=%s | errors=%s",
                 request.url.path, body, [
                     {"loc": e.get("loc"), "msg": e.get("msg")} for e in exc.errors()
                 ])
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


# Serve the main HTML file
# @app.get("/", response_class=FileResponse)
# async def get_index():
#     return "index.html" 

# Serve the CSS file
@app.get("/styles.css", response_class=FileResponse)
async def get_styles():
    return "styles.css"

# Serve the JavaScript file
@app.get("/script.js", response_class=FileResponse)
async def get_script():
    return "script.js"

MAX_TURN = 6 
MAX_SESSION = 500

class ChatRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    session_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), max_length=64)


_session: Dict[str, Deque[Dict]] = defaultdict(lambda: deque(maxlen=MAX_TURN *2))# *2 because each turn is 2 message

_groq_client = None

def get_groq_client():
    # Create groq client lazielt, once and reuse it
    global _groq_client
    if _groq_client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            logger.warning("GROQ_API_KEY not set in environment variables")
            return None
        _groq_client = Groq(api_key=api_key)
    return _groq_client




# System Prompt with your CV data
SYSTEM_PROMPT = """
You are an AI assistant for Amit Pal, a Data Scientist and ML Engineer based in Nepal.
Your goal is to answer questions about his resume politely and professionally.
Here is the context you need to know about Amit:
- Contact: pal98112016@gmail.com | +977-9847132657
- Profile: Entry-level Data Scientist / ML Engineer with strong hands-on experience in building end-to-end ML and AI systems. Skilled in MLOps, RAG, deploying production pipelines with Docker, AWS, CI/CD.
- Skills: Python, SQL, Scikit-learn, LightGBM, RAG, Embeddings, LLMs, Docker, GitHub Actions, AWS, MongoDB, FastAPI, Streamlit.
- Projects: 
  1. Kheti Agent API (Agri-Fintech RAG System): Built with FastAPI, MongoDB, Redis, and Qdrant. It features bilingual (Nepali/English) conversational memory, Whisper voice-to-text, and KYC integration using MCP servers! (Repo: Amit3729/rag_system)
  2. Vehicle Insurance Prediction (End-to-End MLOps Pipeline using FastAPI, MongoDB, AWS, Docker)
  3. Private RAG System with Interview Booking (FastAPI, Qdrant, LLMs)
- Education: B.Sc. in Computer Science and Software Engineering (Patan College of Professional Studies, 2019-2023).
Keep your answers relatively short, conversational, and direct visitors to hire Amit!
"""

# Groq AI Chatbot API
@app.post("/api/chat")
async def chat_with_bot(payload: ChatRequest):
    client = get_groq_client()
    if client is None:
        logger.warning("GROQ API Key not set in environment variables")
        return {"reply": "Hi! I am the AI bot. Currently, Unable to respond Sorry!"}

    session_id = payload.session_id or str(uuid.uuid4())

    if session_id not in _session and len(_session) >= MAX_SESSION:
        _session.pop(next(iter(_session)))   # drop the oldest session

    history = _session[session_id]
    #system prompt + remember turn + new question
    message: List[Dict] = (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + list(history)
        + [{"role": "user", "content": payload.text}]
    )
    try:
        completion = client.chat.completions.create(
            messages=message,
            model="openai/gpt-oss-120b",
            temperature=0.7,
            max_tokens=250
        )

        reply = completion.choices[0].message.content

        #only rememmber the exchange if it actually succceeded
        history.append({"role": "user", "content": payload.text})
        history.append({"role": "assistant", "content": reply})

        logger.info("Chat reply generated (session=%s, turn=%d)", session_id[:8], len(history)//2)
        return {"reply": reply, "session_id": session_id}
    except Exception:
        logger.exception("Groq API error")
        return {"reply": "Sorry, I encountered a problem. Please try again."}
    


# Placeholder API for future ML Prediction Demo
@app.post("/api/predict")
async def predict_insurance(data: dict):
    # Imagine calling LightGBM or Scikit-learn here!
    return {"prediction": "Likely to purchase (Dummy Response)"}

@app.get("/api/health")
async def health_check():
    return {"status": "API is healthy and running!"}

@app.get("/")
async def viewpage():
    return FileResponse("index.html")

if __name__ == "__main__":
    import uvicorn
    # Run the server on port 8000
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
