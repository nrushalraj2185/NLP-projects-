# 🤖 Smart Resume AI - Conversational Chatbot

## Overview

The **Smart Resume AI Chatbot** is a conversational AI assistant that provides intelligent, context-aware interactions about resume content. Unlike traditional Q&A systems, this chatbot:

- ✅ **Remembers the conversation** - Full context memory throughout the session
- ✅ **Understands follow-ups** - Handles "tell me more", "what else?", etc.
- ✅ **Provides smart suggestions** - Contextual question recommendations
- ✅ **No re-uploading needed** - Upload once, ask unlimited questions
- ✅ **Natural conversation** - Conversational tone with greetings, thanks, etc.

---

## 🚀 Quick Start

### 1. Start the Server
```bash
cd "Z:/Ethnotech 26/smart_resume_ai"
python app.py
```

### 2. Access the Chatbot
Open your browser and navigate to:
```
http://localhost:8000/static/chat.html
```

Or click **"Try the AI Chatbot →"** from the main page.

### 3. Start Chatting
1. Upload a resume (PDF or DOCX)
2. Click **"Start Chatting"**
3. Ask questions naturally!

---

## 💬 Example Conversations

### Basic Questions
```
You: What are the candidate's skills?
AI: Based on what I found: Python, FastAPI, Machine Learning, PyTorch, 
    Transformers, REST APIs, Docker

You: Tell me more about their experience
AI: The candidate has worked at TechCorp as a Senior Developer for 3 years, 
    focusing on AI/ML applications...
```

### Follow-up Questions
```
You: What projects have they worked on?
AI: The resume mentions several projects including a Resume Intelligence 
    System, an AI chatbot, and a document processing pipeline.

You: Tell me more
AI: Based on the resume, here are more details: The Resume Intelligence 
    System uses FastAPI and Transformers for document analysis...

You: What technologies were used?
AI: Python, FastAPI, PyTorch, Transformers, sentence-transformers, PyMuPDF
```

### Conversational Interactions
```
You: Hi
AI: Hello! How can I help you with this resume today?

You: What's the email?
AI: john.doe@email.com

You: Thanks!
AI: You're welcome! Feel free to ask anything else about this resume.
```

---

## 🎯 Key Features

### 1. **Session Management**
- Each resume upload creates a unique session
- Conversation history is maintained throughout the session
- No need to re-upload the resume for follow-up questions

### 2. **Context-Aware Responses**
- Understands conversational patterns (greetings, thanks, follow-ups)
- Maintains context from previous questions
- Provides relevant follow-up suggestions

### 3. **Smart Suggestions**
The chatbot provides contextual suggestions based on your questions:
- After asking about skills → Suggests project-related questions
- After asking about experience → Suggests achievement questions
- After asking about education → Suggests academic questions

### 4. **Confidence Scoring**
- High confidence (>80%): Direct answer
- Medium confidence (50-80%): "Based on what I found..."
- Low confidence (<50%): Indicates uncertainty and suggests rephrasing

### 5. **Beautiful UI**
- Modern dark theme with smooth animations
- Message bubbles with timestamps
- Typing indicators
- Suggestion chips for quick questions
- Responsive design

---

## 🔧 API Endpoints

### Create Chat Session
```bash
POST /chatbot/session
Content-Type: multipart/form-data

Body:
  resume_file: <file>

Response:
{
  "session_id": "uuid-string",
  "conversation_history": [...],
  "message": "Session created successfully"
}
```

### Send Message
```bash
POST /chatbot/message
Content-Type: application/json

Body:
{
  "session_id": "uuid-string",
  "message": "What are the skills?"
}

Response:
{
  "answer": "Python, FastAPI, Machine Learning...",
  "confidence": 0.92,
  "suggestions": ["What projects?", "Years of experience?"],
  "session_valid": true,
  "conversation_history": [...]
}
```

### Get Conversation History
```bash
GET /chatbot/history/{session_id}

Response:
{
  "conversation_history": [
    {
      "role": "assistant",
      "content": "Welcome message...",
      "timestamp": "2026-02-09T10:00:00"
    },
    {
      "role": "user",
      "content": "What are the skills?",
      "timestamp": "2026-02-09T10:01:00"
    }
  ]
}
```

### Clear Session
```bash
DELETE /chatbot/session/{session_id}

Response:
{
  "message": "Session cleared successfully"
}
```

### Get Session Info
```bash
GET /chatbot/session/{session_id}/info

Response:
{
  "session_id": "uuid-string",
  "created_at": "2026-02-09T10:00:00",
  "last_activity": "2026-02-09T10:05:00",
  "message_count": 8,
  "has_resume": true
}
```

---

## 🎨 UI Components

### Upload Screen
- Drag-and-drop file upload
- File format validation
- Feature highlights
- Smooth animations

### Chat Interface
- Message bubbles (user vs assistant)
- Avatar icons
- Timestamps
- Typing indicators
- Confidence indicators for uncertain answers

### Suggestions Bar
- Contextual question chips
- Click to auto-fill and send
- Dynamic based on conversation

### Input Area
- Auto-focus on load
- Enter to send
- Keyboard shortcuts (Ctrl+K to focus)
- Send button with hover effects

---

## 🧠 How It Works

### 1. Session Creation
```python
# User uploads resume
session_id = chatbot.create_session(resume_text)

# Welcome message generated
welcome = "Hi John! I've analyzed the resume..."
```

### 2. Message Processing
```python
# User sends message
response = chatbot.chat(session_id, "What are the skills?")

# AI processes with context
- Check for conversational patterns (hi, thanks, etc.)
- Use QA model for specific questions
- Generate contextual suggestions
- Add to conversation history
```

### 3. Context Memory
```python
# Conversation history stored per session
sessions[session_id] = {
    "resume_text": "...",
    "conversation_history": [
        {"role": "assistant", "content": "Welcome..."},
        {"role": "user", "content": "What are skills?"},
        {"role": "assistant", "content": "Python, FastAPI..."}
    ]
}
```

---

## 🚀 Advanced Features

### Keyboard Shortcuts
- **Enter**: Send message
- **Ctrl/Cmd + K**: Focus input
- **Escape**: Blur input

### Conversational Patterns Supported
- Greetings: "hi", "hello", "hey"
- Thanks: "thank you", "thanks"
- Follow-ups: "tell me more", "elaborate", "explain"
- Contextual: "what else?", "more details"

### Smart Suggestion Categories
1. **Skill-based**: Projects, experience, certifications
2. **Experience-based**: Achievements, technologies, duration
3. **Education-based**: Major, graduation, achievements
4. **Contact-based**: Location, portfolio, LinkedIn

---

## 📊 Performance

- **Session Creation**: ~500-1000ms (includes text extraction)
- **Message Response**: ~200-800ms (QA model inference)
- **Memory Usage**: ~2-3GB (models loaded once)
- **Concurrent Sessions**: Unlimited (in-memory storage)

---

## 🔮 Future Enhancements

### Planned Features
1. **Persistent Storage**: Database for conversation history
2. **Multi-Resume Comparison**: Compare multiple resumes in one chat
3. **Export Conversations**: Download chat history as PDF/JSON
4. **Voice Input**: Speech-to-text for questions
5. **Advanced NLP**: Better context understanding with GPT integration
6. **Resume Insights**: Proactive suggestions and analysis
7. **Multi-language Support**: Support for non-English resumes

### Potential Integrations
- **OpenAI GPT**: More natural conversations
- **Database**: PostgreSQL/MongoDB for persistence
- **Authentication**: User accounts and saved sessions
- **Analytics**: Track common questions and insights

---

## 🐛 Troubleshooting

### Chatbot not responding?
- Check if server is running (`python app.py`)
- Verify session was created successfully
- Check browser console for errors

### Low confidence answers?
- Question may be too vague - try being more specific
- Information might not be in the resume
- Try rephrasing the question

### Session lost?
- Sessions are in-memory only (cleared on server restart)
- Upload the resume again to create a new session

---

## 📝 Code Structure

```
smart_resume_ai/
├── utils/
│   └── chatbot.py          # Conversational AI logic
├── static/
│   ├── chat.html           # Chat interface
│   ├── chat.css            # Chat styling
│   └── chat.js             # Chat functionality
└── app.py                  # API endpoints
```

### Key Classes

**ConversationalChatbot** (`utils/chatbot.py`)
- `create_session()`: Initialize chat session
- `chat()`: Process messages with context
- `_generate_response()`: AI response generation
- `_generate_suggestions()`: Smart follow-up suggestions

---

## 🎓 Example Use Cases

### 1. Recruiter Screening
```
"What's the candidate's total experience?"
"What are their top 3 skills?"
"Have they worked with Python?"
"What's their education background?"
```

### 2. Detailed Analysis
```
"Tell me about their recent projects"
"What technologies have they used?"
"What are their key achievements?"
"What certifications do they have?"
```

### 3. Contact & Logistics
```
"What's their email?"
"Where are they located?"
"Do they have a LinkedIn profile?"
"What's their phone number?"
```

---

## ✅ Comparison: Classic vs Chatbot Mode

| Feature | Classic Mode | Chatbot Mode |
|---------|-------------|--------------|
| **Interaction** | Single Q&A | Continuous conversation |
| **Context Memory** | ❌ None | ✅ Full history |
| **Follow-ups** | ❌ Re-upload needed | ✅ Seamless |
| **Suggestions** | ❌ None | ✅ Smart suggestions |
| **Tone** | Technical | Conversational |
| **Use Case** | Quick queries | In-depth analysis |

---

## 📄 License

MIT License - Same as main project

---

## 🙏 Credits

Built with:
- **FastAPI** - Web framework
- **Hugging Face Transformers** - AI models
- **PyTorch** - Deep learning backend
- **DistilBERT** - Question answering model

---

**Ready to chat with resumes? Start the server and visit `/static/chat.html`!** 🚀
