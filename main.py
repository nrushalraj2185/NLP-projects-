from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.parser import extract_text
from services.matcher import match_resume_job
from services.qa import answer_question
from services.gemini_agent import get_agent, ResumeAnalystAgent # Use the new superior agent
from core.config import settings
import uvicorn
import os

app = FastAPI(title="Smart Resume Intelligence API")

# Add CORS middleware for better frontend support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for chatbot
class ChatMessage(BaseModel):
    session_id: str
    message: str

class SessionResponse(BaseModel):
    session_id: str
    welcome_message: str
    conversation_history: list

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.post("/match")
async def match_resume(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    text = await resume_file.read()
    resume_text = extract_text(text, resume_file.filename)
    match_score = match_resume_job(resume_text, job_description)
    return {"match_score": match_score}

@app.post("/qa")
async def qa_from_resume(
    resume_file: UploadFile = File(...),
    question: str = Form(...)
):
    text = await resume_file.read()
    resume_text = extract_text(text, resume_file.filename)
    answer = answer_question(resume_text, question)
    return {"answer": answer}

# ===== CHATBOT ENDPOINTS =====

@app.post("/chatbot/session")
async def create_chat_session(resume_file: UploadFile = File(...)):
    """Create a new chatbot session with resume context"""
    try:
        text = await resume_file.read()
        resume_text = extract_text(text, resume_file.filename)
        
        # Get the initialized agent
        agent = get_agent()
        
        # Create dedicated session
        session_id, welcome_msg = agent.create_session(resume_text)
        conversation_history = agent.get_history(session_id)
        
        return {
            "session_id": session_id,
            "conversation_history": conversation_history,
            "message": "Session created successfully"
        }
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve)) # API Key missing
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")

@app.post("/chatbot/message")
async def send_chat_message(chat_message: ChatMessage):
    """Send a message to the chatbot and get AI response"""
    try:
        agent = get_agent()
        response = agent.chat(chat_message.session_id, chat_message.message)
        
        if not response.get("valid", False):
             # Try to provide a more specific error if available
            raise HTTPException(status_code=404, detail=response.get("error", "Session not found"))
        
        return {
            "answer": response["answer"],
            "suggestions": response.get("suggestions", []),
            "session_valid": True,
            "conversation_history": agent.get_history(chat_message.session_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/chatbot/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get conversation history for a session"""
    agent = get_agent()
    history = agent.get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found or empty")
    return {"conversation_history": history}

@app.delete("/chatbot/session/{session_id}")
async def delete_chat_session(session_id: str):
    """Clear a chat session"""
    agent = get_agent()
    agent.clear_session(session_id)
    return {"message": "Session cleared successfully"}

@app.get("/chatbot/session/{session_id}/info")
async def get_session_info(session_id: str):
    """Get session metadata"""
    # Simply confirm existence for now
    agent = get_agent()
    history = agent.get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "message_count": len(history),
        "has_resume": True,
        "agent_type": "Google Gemini High-Quality Agent"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
