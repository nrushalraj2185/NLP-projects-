from utils.skill_extractor import extract_skills

def analyze_skill_gap(resume_text, job_text):
    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_text))
    missing_skills = list(job_skills - resume_skills)
    matched_skills = list(resume_skills & job_skills)
    return {
        "missing_skills": sorted(missing_skills),
        "matched_skills": sorted(matched_skills)
    }
