from transformers import pipeline
from core.config import settings

qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")

def answer_question(text, question):
    result = qa_pipeline(question=question, context=text)
    return result["answer"]
