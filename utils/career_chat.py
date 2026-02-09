from transformers import pipeline

chat_pipeline = pipeline("text-generation", model="gpt2")

def career_advisor_bot(query):
    intro = "You're a helpful career coach. Answer the user's question based on job market trends and resume best practices.\n\n"
    full_prompt = intro + query
    output = chat_pipeline(full_prompt, max_length=150, do_sample=True)
    return output[0]["generated_text"]
