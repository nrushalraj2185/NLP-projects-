import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import fitz # PyMuPDF
import docx
import pytesseract
from PIL import Image
import io
from datetime import datetime

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

SYSTEM_INSTRUCTION = f"""You are Nova AI, a helpful and advanced assistant. 
Today's date is {datetime.now().strftime('%A, %B %d, %Y')}. 
Current time is {datetime.now().strftime('%H:%M:%S')}.
You should use this information to answer questions about the current date/time correctly."""

model = genai.GenerativeModel(
    'gemini-flash-latest',
    system_instruction=SYSTEM_INSTRUCTION
)

app = FastAPI(title="Giant Exoplanet Chatbot API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specify the actual origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.get("/")
async def root():
    return {"message": "Chatbot API is running"}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Simple conversation logic
        chat_session = model.start_chat(history=request.history)
        response = chat_session.send_message(request.message)
        return {
            "response": response.text,
            "history": request.history + [
                {"role": "user", "parts": [request.message]},
                {"role": "model", "parts": [response.text]}
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = ""
        filename = file.filename.lower()
        file_bytes = await file.read()
        
        if filename.endswith('.pdf'):
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                content += page.get_text()
        elif filename.endswith('.docx'):
            doc = docx.Document(io.BytesIO(file_bytes))
            for para in doc.paragraphs:
                content += para.text + "\n"
        elif filename.endswith(('.png', '.jpg', '.jpeg')):
            image = Image.open(io.BytesIO(file_bytes))
            content = pytesseract.image_to_string(image)
        else:
            return {"error": "Unsupported file format"}
            
        return {"content": content, "filename": file.filename}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
