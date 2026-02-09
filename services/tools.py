import google.generativeai as genai
from core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

class ResumeTools:
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            raise ValueError("Google API Key required for Resume Tools")
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    def extract_skills(self, text: str):
        """Extracts technical and soft skills from text."""
        prompt = f"""
        Extract all technical skills, soft skills, and tools from the following text.
        Return ONLY a JSON list of strings, e.g. ["Python", "Leadership", "Excel"].
        Do not output markdown or explanations.
        
        Text: {text[:4000]}
        """
        try:
            response = self.model.generate_content(prompt)
            # robust cleanup
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Skill extraction failed: {e}")
            return []

    def analyze_gap(self, resume_text: str, job_description: str):
        """Analyzes gaps between resume and job description."""
        prompt = f"""
        Compare the below Resume and Job Description.
        Identify matched skills and missing skills.
        Return ONLY valid JSON:
        {{
            "matched_skills": ["skill1", "skill2"],
            "missing_skills": ["skill3", "skill4"],
            "score": 85
        }}

        Resume: {resume_text[:2000]}
        Job Description: {job_description[:2000]}
        """
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Gap analysis failed: {e}")
            return {"error": str(e)}

    def rewrite_section(self, text: str, target_keywords: list):
        """Rewrites text to include keywords naturally."""
        prompt = f"""
        Rewrite this resume section to include keywords: {', '.join(target_keywords)}.
        Keep it professional.
        original: {text}
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Rewrite failed: {e}")
            return text

    def suggest_roles(self, resume_text: str):
        """Suggests suitable job roles based on resume."""
        prompt = f"""
        Suggest 5 job titles for this resume.
        Return ONLY a JSON list of strings, e.g. ["Software Engineer", "Data Analyst"].
        No markdown.
        
        Resume: {resume_text[:3000]}
        """
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            return json.loads(clean_text)
        except Exception as e:
            logger.error(f"Role suggestion failed: {e}")
            return []

# Singleton
resume_tools = ResumeTools()
