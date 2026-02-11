from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

settings = Settings()
