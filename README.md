# Smart Resume Intelligence System (SRIS)

A modern web application powered by FastAPI and AI for intelligent resume analysis, job matching, and **conversational AI chatbot**.

## ✨ Features

- 🤖 **AI Chatbot** - NEW! Conversational assistant with context memory and smart follow-ups
- 🎯 **Resume-Job Matching** - Get AI-powered compatibility scores between resumes and job descriptions
- 💬 **Resume Q&A** - Ask questions and extract specific information from resumes
- 📄 **Multi-Format Support** - Works with PDF and DOCX files
- 🎨 **Beautiful UI** - Modern, responsive web interface with real-time progress tracking
- 🤖 **Advanced AI** - Uses SentenceTransformer and Hugging Face models

## 🚀 Quick Start

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional but Recommended)
Create a `.env` file to use Google Gemini for the best chatbot experience:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```
*If no key is provided, the system falls back to a local model.*

### 3. Run the Application
```bash
python main.py
```

### 4. Open in Browser
Navigate to: **http://localhost:8000**

## 📂 Project Structure
```
smart_resume_ai/
├── backend/
│   ├── main.py        # Application entry point
│   ├── core/          # Configuration and settings
│   └── services/      # Business logic (Chatbot, Matcher, Parser)
├── frontend/ (static) # Web interface files
└── requirements.txt   # Dependencies
```

## 🎯 How to Use

### Resume Matching
1. Click on the **"Resume Matching"** tab
2. Upload a resume (PDF or DOCX)
3. Paste the job description
4. Click **"Analyze Match"**
5. View your compatibility score with detailed interpretation

### Resume Q&A
1. Click on the **"Ask Questions"** tab
2. Upload a resume (PDF or DOCX)
3. Type your question (e.g., "What is the candidate's email?")
4. Click **"Find Answer"**
5. Get instant AI-powered answers

## 📋 Supported File Formats

- ✅ PDF (`.pdf`)
- ✅ Word Documents (`.docx`)
- ⚠️ Images (`.png`, `.jpg`, `.jpeg`) - Requires Tesseract OCR installation

## 🔧 Environment Variables

Create a `.env` file (optional):
```
OPENAI_API_KEY=your_key_here  # optional, not currently used
```

## 🌐 API Endpoints

The application also provides REST API endpoints:

- `GET /` - Web interface
- `POST /match` - Resume-job matching (form fields: `resume_file`, `job_description`)
- `POST /qa` - Resume Q&A (form fields: `resume_file`, `question`)
- `GET /docs` - Interactive API documentation (Swagger UI)

### API Example
```bash
curl -X POST http://localhost:8000/match \
  -F "resume_file=@sample_resume.pdf" \
  -F "job_description=We are hiring a Python developer..."
```

## 🛠️ Tech Stack

- **Backend**: FastAPI, Uvicorn
- **AI/ML**: PyTorch, Transformers, Sentence-Transformers
- **Document Processing**: PyMuPDF, python-docx, pytesseract
- **Frontend**: Vanilla HTML, CSS, JavaScript

## 📊 Models Used

- **Resume Matching**: `sentence-transformers/all-MiniLM-L6-v2`
- **Question Answering**: `distilbert-base-uncased-distilled-squad`

## 📝 Notes

- First run will download AI models (~500MB) - this is normal
- Subsequent runs will be instant as models are cached
- For image-based resumes, install Tesseract OCR separately

## 📄 License

MIT

