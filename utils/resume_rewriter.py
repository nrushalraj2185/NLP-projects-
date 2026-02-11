from transformers import pipeline

generator = pipeline("text2text-generation", model="google/flan-t5-base")

def rewrite_resume_section(section_text, target_keywords):
    prompt = (
        f"Rewrite this resume section to better align with the following job keywords: {', '.join(target_keywords)}. "
        f"Preserve the original meaning and facts:\n\n{section_text}"
    )
    output = generator(prompt, max_length=512, do_sample=False)
    return output[0]["generated_text"]
