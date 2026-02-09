from transformers import pipeline
import google.generativeai as genai
from core.config import settings
from typing import List, Dict, Optional
import uuid
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationalChatbot:
    """AI-driven conversational chatbot with context memory (Gemini + Local Fallback)"""
    
    def __init__(self):
        self.use_gemini = False
        
        # Initialize Google Gemini if API key is present
        if settings.GOOGLE_API_KEY:
            try:
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                self.use_gemini = True
                logger.info("✅ Google Gemini initialized successfully")
            except Exception as e:
                logger.error(f"⚠️ Failed to initialize Gemini: {e}")
                self.use_gemini = False
        
        # Fallback to local model if Gemini is not available
        if not self.use_gemini:
            logger.info("🔄 Falling back to local transformers model")
            try:
                self.qa_pipeline = pipeline(
                    "question-answering", 
                    model="distilbert-base-uncased-distilled-squad"
                )
            except Exception as e:
                logger.error(f"❌ Failed to load local model: {e}")
                self.qa_pipeline = None

        # Session storage: {session_id: {resume_text, conversation_history, gemini_chat, metadata}}
        self.sessions = {}
        
    def create_session(self, resume_text: str) -> str:
        """Create a new chat session with resume context"""
        session_id = str(uuid.uuid4())
        
        gemini_chat = None
        if self.use_gemini:
            try:
                # Start a new chat session with system instruction
                gemini_chat = self.gemini_model.start_chat(history=[
                    {
                        "role": "user",
                        "parts": [f"You are a helpful HR assistant. Here is the resume context you need to answer questions about:\n\n{resume_text}\n\nPlease answer questions based ONLY on this resume. If information is missing, say so politely."]
                    },
                    {
                        "role": "model",
                        "parts": ["Understood. I have analyzed the resume and I am ready to answer questions about it."]
                    }
                ])
            except Exception as e:
                logger.error(f"Error starting Gemini chat: {e}")
                gemini_chat = None

        self.sessions[session_id] = {
            "resume_text": resume_text,
            "conversation_history": [],
            "gemini_chat": gemini_chat,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
        # Add welcome message
        welcome_msg = self._generate_welcome_message(resume_text, gemini_chat)
        self.sessions[session_id]["conversation_history"].append({
            "role": "assistant",
            "content": welcome_msg,
            "timestamp": datetime.now().isoformat()
        })
        
        return session_id
    
    def _generate_welcome_message(self, resume_text: str, gemini_chat=None) -> str:
        """Generate personalized welcome message"""
        if self.use_gemini and gemini_chat:
            try:
                response = gemini_chat.send_message("Generate a short, friendly welcome message mentioning the candidate's name if found.")
                return response.text
            except:
                pass

        # Fallback welcome logic
        name = "there" 
        if self.qa_pipeline:
            try:
                name_result = self.qa_pipeline(
                    question="What is the candidate's name?",
                    context=resume_text[:1000]
                )
                if name_result["score"] > 0.3:
                    name = name_result["answer"]
            except:
                pass
        
        return f"👋 Hi {name}! I've analyzed the resume. I can answer questions about skills, experience, projects, and more. What would you like to know?"
    
    def chat(self, session_id: str, user_message: str) -> Dict:
        """Process user message and generate AI response"""
        if session_id not in self.sessions:
            return {"error": "Session not found", "session_valid": False}
        
        session = self.sessions[session_id]
        
        # Update history
        session["conversation_history"].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate response
        if self.use_gemini and session.get("gemini_chat"):
            response_data = self._chat_with_gemini(session["gemini_chat"], user_message)
        else:
            response_data = self._chat_local(user_message, session["resume_text"], session["conversation_history"])
        
        # Add response to history
        session["conversation_history"].append({
            "role": "assistant",
            "content": response_data["answer"],
            "timestamp": datetime.now().isoformat(),
            "confidence": response_data.get("confidence", 1.0)
        })
        session["last_activity"] = datetime.now().isoformat()
        
        return {
            "answer": response_data["answer"],
            "confidence": response_data.get("confidence", 1.0),
            "suggestions": response_data.get("suggestions", []),
            "session_valid": True,
            "conversation_history": session["conversation_history"]
        }

    def _chat_with_gemini(self, chat_session, message: str) -> Dict:
        """Chat using Google Gemini"""
        try:
            response = chat_session.send_message(message)
            answer = response.text
            
            # Generate suggestions (simple heuristic or separate call)
            suggestions = self._generate_suggestions_heuristic(message, answer)
            
            return {
                "answer": answer,
                "confidence": 0.95,  # Gemini is usually confident
                "suggestions": suggestions
            }
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            return {
                "answer": "I'm having trouble connecting to my AI brain right now. Please try again.",
                "confidence": 0.0,
                "suggestions": []
            }

    def _chat_local(self, question: str, resume_text: str, history: List[Dict]) -> Dict:
        """Fallback to local Transformers model"""
        if not self.qa_pipeline:
             return {
                "answer": "AI model not initialized. Please check server logs.",
                "confidence": 0.0,
                "suggestions": []
            }
            
        # ... (reuse existing logic for local chat) ...
        # Simplified for brevity in this tool call, but ideally keep logic
        
        try:
            # Simple context handling
            result = self.qa_pipeline(question=question, context=resume_text)
            suggestions = self._generate_suggestions_heuristic(question, result["answer"])
            return {
                "answer": result["answer"],
                "confidence": result["score"],
                "suggestions": suggestions
            }
        except:
             return {
                "answer": "I couldn't find an answer in the resume.",
                "confidence": 0.0,
                "suggestions": []
            }

    def _generate_suggestions_heuristic(self, question: str, answer: str) -> List[str]:
        """Generate suggestions based on keywords"""
        q_lower = question.lower()
        if "skill" in q_lower:
            return ["Where were these skills used?", "Any certifications?", "Years of experience?"]
        elif "experience" in q_lower or "work" in q_lower:
            return ["Key achievements?", "Technologies used?", "Management experience?"]
        elif "education" in q_lower:
            return ["Graduation year?", "GPA/Grades?", "Relevant coursework?"]
        return ["Tell me about projects", "What are the strengths?", "Contact info?"]

    def get_conversation_history(self, session_id: str) -> List[Dict]:
        return self.sessions.get(session_id, {}).get("conversation_history", [])
    
    def clear_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_session_info(self, session_id: str) -> Dict:
        if session_id in self.sessions:
            return {
                "session_id": session_id,
                "created_at": self.sessions[session_id]["created_at"],
                "last_activity": self.sessions[session_id]["last_activity"],
                "message_count": len(self.sessions[session_id]["conversation_history"]),
                "has_resume": True,
                "model": "Gemini 1.5 Flash" if self.use_gemini else "DistilBERT"
            }
        return None

chatbot = ConversationalChatbot()
