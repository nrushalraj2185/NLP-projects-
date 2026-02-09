from sentence_transformers import SentenceTransformer, util
from core.config import settings

model = SentenceTransformer(settings.EMBEDDING_MODEL)

def match_resume_job(resume_text, job_text):
    embeddings = model.encode([resume_text, job_text], convert_to_tensor=True)
    score = util.cos_sim(embeddings[0], embeddings[1]).item()
    return round(score * 100, 2)
