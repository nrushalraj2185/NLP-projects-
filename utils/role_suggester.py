from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

role_database = [
    "Data Scientist", "ML Engineer", "Cloud Engineer",
    "DevOps Engineer", "Business Analyst", "Software Engineer"
]

def suggest_roles_from_resume(resume_text, top_k=3):
    resume_embed = model.encode(resume_text, convert_to_tensor=True)
    role_embeds = model.encode(role_database, convert_to_tensor=True)
    similarities = util.cos_sim(resume_embed, role_embeds)[0]
    top_indices = similarities.argsort(descending=True)[:top_k]
    return [(role_database[i], round(similarities[i].item(), 3)) for i in top_indices]
