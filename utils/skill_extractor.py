import spacy

nlp = spacy.load("en_core_web_trf")

def extract_skills(text):
    doc = nlp(text)
    skills = set()
    for ent in doc.ents:
        if ent.label_ in {"SKILL", "TECH", "ORG"}:
            skills.add(ent.text.lower())
    return list(skills)
