# 🚀 Quick Start Guide - Smart Resume AI

## Start the Server (One Command)

```bash
python app.py
```

**That's it!** The server will start on `http://localhost:8000`

---

## Test the API

### Option 1: Interactive Documentation (Recommended)
Open your browser and go to:
```
http://localhost:8000/docs
```

You'll see a beautiful Swagger UI where you can:
- Upload files directly
- Test endpoints interactively
- See request/response examples

### Option 2: Command Line (cURL)

**Test Resume Matching:**
```bash
curl -X POST http://localhost:8000/match \
  -F "resume_file=@your_resume.pdf" \
  -F "job_description=Looking for a Python developer with 3+ years experience in FastAPI and machine learning..."
```

**Test Question Answering:**
```bash
curl -X POST http://localhost:8000/qa \
  -F "resume_file=@your_resume.pdf" \
  -F "question=What programming languages does the candidate know?"
```

### Option 3: Python Requests

```python
import requests

# Resume Matching
with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/match',
        files={'resume_file': f},
        data={'job_description': 'We need a Python developer...'}
    )
    print(f"Match Score: {response.json()['match_score']}%")

# Question Answering
with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/qa',
        files={'resume_file': f},
        data={'question': 'What is the candidate\'s email?'}
    )
    print(f"Answer: {response.json()['answer']}")
```

---

## Supported File Types

- ✅ **PDF** (`.pdf`) - Fully supported
- ✅ **Word** (`.docx`) - Fully supported  
- ⚠️ **Images** (`.png`, `.jpg`, `.jpeg`) - Requires Tesseract OCR installation

---

## Common Issues

### "Module not found" error
```bash
pip install -r requirements.txt
```

### Port 8000 already in use
Change the port in `app.py`:
```python
uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
```

### Models downloading slowly
First run downloads ~500MB of ML models. Be patient! Subsequent runs are instant.

---

## Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

---

**Need help?** Check `PROJECT_READINESS_REPORT.md` for detailed information.
