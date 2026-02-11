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
    
    # Persona for Resume Analysis (The "Toolkit" Subset)
    SYSTEM_INSTRUCTION_RESUME = """
    You are the "Intelligent Career Analyzer" (ICA) - Resume Specialist.
    FOCUS: Gap Analysis, Resume Rewriting, and Skill Extraction.
    
    You have a resume context. Use it to:
    1. **Gap Analyzer**: Compare their specific skills against target roles.
    2. **Resume Rewriter**: Rewrite sections for impact.
    3. **Skill Extractor**: List their hard/soft skills.
    
    Be precise, honest, and constructive.
    """

    # Persona for General Career Advice (No Resume)
    SYSTEM_INSTRUCTION_GENERAL = """
    You are the "Intelligent Career Analyzer" (ICA) - Career Strategist.
    FOCUS: Career mapping, Role suggestions, and Industry trends.
    
    You DO NOT have a resume. Ask probing questions to understand the user's:
    - Interests and passions
    - Current expertise level
    - Career goals
    
    Then provide:
    1. **Role Suggestions**: Recommend paths based on their answers.
    2. **Career Advice**: General guidance on industries and growth.
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
            
            # Prioritize gemini-1.5-flash which has better free tier limits
            # Order matters: check for 1.5-flash specifically first
            target_model = None
            for m in available_models:
                if 'gemini-1.5-flash' in m and 'latest' not in m:
                    target_model = m
                    break
            
            if not target_model:
                # Fallback to any flash model
                for m in available_models:
                    if 'flash' in m:
                        target_model = m
                        break
            
            # If still nothing, take the first available
            if not target_model:
                target_model = available_models[0]

            self.model_name = target_model
            logger.info(f"✅ ResumeAnalystAgent forcing model: {self.model_name}")
            
            logger.info(f"✅ ResumeAnalystAgent initialized with {self.model_name}")
            
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Gemini: {e}")
            raise e

        # In-memory session storage
        self.sessions = {}

    def create_session(self, resume_text: str = None) -> tuple[str, str, list[str]]:
        """Starts a new session. If resume_text is None, starts a General Advisor session."""
        session_id = str(uuid.uuid4())
        
        try:
            if resume_text:
                # --- RESUME MODE ---
                initial_history = [
                    {"role": "user", "parts": [f"{self.SYSTEM_INSTRUCTION_RESUME}\n\nRESUME:\n{resume_text}"]},
                    {"role": "model", "parts": ["Resume analyzed. Ready for Gap Analysis, Rewriting, and Skill Extraction."]}
                ]
                welcome_prompt = "Briefly summarize the candidate's profile and list the 3 Toolkit features (Gap Analysis, Rewrite, Skills) as ready."
                
                initial_suggestions = [
                    "Perform Gap Analysis",
                    "Rewrite my Summary",
                    "Extract Skills List",
                    "Critique this resume"
                ]
            else:
                # --- GENERAL ADVISOR MODE ---
                initial_history = [
                    {"role": "user", "parts": [self.SYSTEM_INSTRUCTION_GENERAL]},
                    {"role": "model", "parts": ["Ready to advise on career paths and roles."]}
                ]
                welcome_prompt = "Introduce yourself as ICA Career Strategist. Ask the user about their current field or interests to start suggesting roles."
                
                initial_suggestions = [
                    "Suggest high-growth roles",
                    "How do I switch to AI?",
                    "What are top skills for 2026?",
                    "Help me plan my career"
                ]

            chat_session = self.model.start_chat(history=initial_history)
            
            try:
                # Attempt to generate a custom welcome message
                welcome_response = chat_session.send_message(welcome_prompt)
                welcome_msg = welcome_response.text
            except Exception as e:
                logger.warning(f"⚠️ API Welcome Failed (likely Quota): {e}")
                # Fallback to a static welcome message so the UI still loads!
                welcome_msg = "Hello! I am the Intelligent Career Analyzer (ICA). My AI service makes me slightly delayed at the moment due to high traffic, but I am ready to help you with your career and resume needs. Please try asking a question!"

            self.sessions[session_id] = {
                "chat_session": chat_session,
                "resume_text": resume_text,
                "history": [],
                "created_at": datetime.now().isoformat()
            }
            
            self.sessions[session_id]["history"].append({
                "role": "assistant",
                "content": welcome_msg,
                "timestamp": datetime.now().isoformat()
            })

            return session_id, welcome_msg, initial_suggestions

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

            # Generate smart follow-up suggestions
            suggestions = self._generate_suggestions(session)

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

    def _generate_suggestions(self, session) -> List[str]:
        """Generates context-aware follow-up suggestions."""
        # Check if we are in Resume Mode or General Mode
        is_resume_mode = session.get("resume_text") is not None
        
        if is_resume_mode:
            return [
                "Perform Gap Analysis",
                "Suggest Interview Questions",
                "Rewrite this section",
                "What skills am I missing?"
            ]
        else:
            return [
                "Suggest other roles",
                "What skills are needed?",
                "How to prepare for interviews?",
                "Tell me about industry trends"
            ]

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
