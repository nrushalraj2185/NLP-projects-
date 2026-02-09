import google.generativeai as genai
from core.config import settings
import logging
from typing import List, Dict, Optional
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResumeAnalystAgent:
    """
    A specialized AI agent for resume analysis and recruitment conversations.
    Powered exclusively by Google Gemini.
    """
    
    SYSTEM_INSTRUCTION = """
    You are an Expert HR Consultant and Senior Technical Recruiter with 15+ years of experience.
    Your role is to analyze resumes, evaluate candidates, and assist hiring managers.

    CONTEXT:
    You have been provided with a candidate's resume text. All your answers must be based on this specific resume.

    YOUR CAPABILITIES:
    1. **Deep Analysis**: Identify strengths, weaknesses, and gaps in the candidate's profile.
    2. **Fact Extraction**: Instantly retrieve skills, dates, companies, and education details.
    3. **Interview Prep**: Suggest specific, hard-hitting interview questions based on the resume's claims.
    4. **Role Matching**: Evaluate how well the candidate fits a hypothetical or description job description.
    5. **Tone**: Professional, insightful, objective, and helpful. Avoid generic fluff.

    GUIDELINES:
    - If information is missing from the resume, explicitly state: "The resume does not mention..."
    - Do not hallucinate or invent details.
    - Be concise but thorough. Use bullet points for readability.
    - If asked about "fit", provide a balanced Pro/Con analysis.
    """

    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            logger.error("❌ Google API Key is missing! The ResumeAnalystAgent cannot function.")
            raise ValueError("GOOGLE_API_KEY is required in .env file")

        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            
            # Dynamically find a supported model to avoid 404 errors
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            if not available_models:
                raise ValueError("No models found that support 'generateContent'. Please check your API key permissions.")
            
            # Prefer gemini-1.5-flash or gemini-pro if available, otherwise pick the first one
            preferred_models = ['models/gemini-1.5-flash', 'models/gemini-pro', 'models/gemini-1.0-pro']
            self.model_name = next((m for m in preferred_models if m in available_models), available_models[0])
            
            logger.info(f"✅ ResumeAnalystAgent initialized with {self.model_name}")
            logger.info(f"📋 Available models: {available_models}")

            self.model = genai.GenerativeModel(
                model_name=self.model_name
                # System instructions injected into history for compatibility
            )
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Gemini: {e}")
            raise e

        # In-memory session storage
        self.sessions = {}

    def create_session(self, resume_text: str) -> str:
        """Starts a new analysis session for a specific resume."""
        session_id = str(uuid.uuid4())
        
        try:
            # We seed the chat history with the resume context AND system instruction
            initial_history = [
                {
                    "role": "user",
                    "parts": [f"{self.SYSTEM_INSTRUCTION}\n\nHere is the resume for analysis:\n\n{resume_text}\n\nPlease acknowledge receipt and give a 1-sentence summary of who this candidate is."]
                },
                {
                    "role": "model",
                    "parts": ["Resume received. I have analyzed the document and am ready to provide insights as an Expert HR Consultant."]
                }
            ]

            chat_session = self.model.start_chat(history=initial_history)
            
            # Generate a custom welcome message based on the resume
            welcome_response = chat_session.send_message(
                "Give a brief, professional greeting summarizing the candidate's top 2 skills and asking how I can help evaluate them."
            )
            welcome_msg = welcome_response.text

            self.sessions[session_id] = {
                "chat_session": chat_session,
                "resume_text": resume_text, # Keep raw text just in case
                "history": [], # We'll mirror history for the UI if needed
                "created_at": datetime.now().isoformat()
            }
            
            # Save the welcome interaction to our mirrored history
            self.sessions[session_id]["history"].append({
                "role": "assistant",
                "content": welcome_msg,
                "timestamp": datetime.now().isoformat()
            })

            return session_id, welcome_msg

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise e

    def chat(self, session_id: str, user_message: str) -> Dict:
        """Sends a message to the agent and gets a response."""
        if session_id not in self.sessions:
            return {"error": "Session not found", "valid": False}

        session = self.sessions[session_id]
        chat_session = session["chat_session"]

        try:
            # Send message to Gemini
            response = chat_session.send_message(user_message)
            answer = response.text

            # Update our local mirror of history
            session["history"].append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            })
            session["history"].append({
                "role": "assistant",
                "content": answer,
                "timestamp": datetime.now().isoformat()
            })

            # Generate smart follow-up suggestions using a lightweight helper call
            # This makes the agent feel proactive
            suggestions = self._generate_suggestions(chat_session)

            return {
                "answer": answer,
                "suggestions": suggestions,
                "valid": True
            }

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                "answer": "I encountered an error communicating with the AI service. Please check your connection or API key.",
                "valid": True,
                "error": str(e)
            }

    def _generate_suggestions(self, chat_session) -> List[str]:
        """Asks the model itself for relevant follow-up questions."""
        try:
            # We don't want this strictly in the history flow for the user, 
            # but Gemini maintains history in the object. 
            # For a truly separate suggestions call, we'd strictly need a separate model call 
            # without updating history, or just use a static heuristic to save tokens.
            # For now, let's use a robust static set to keep it fast and cheap.
            return [
                "What are the candidate's key strengths?",
                "Identify any red flags or gaps.",
                "Generate interview questions for this role.",
                "Summarize their experience concisely."
            ]
        except:
            return ["Tell me more about their experience.", "What skills do they lack?"]

    def get_history(self, session_id: str) -> List[Dict]:
        return self.sessions.get(session_id, {}).get("history", [])

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

# Singleton instance
# We strictly initialize this only when needed in main to handle config loading
agent = None

def get_agent():
    global agent
    if agent is None:
        agent = ResumeAnalystAgent()
    return agent
