import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
print(f"🔑 API Key found: {'Yes' if api_key else 'No'}")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env")
    exit(1)

try:
    genai.configure(api_key=api_key)
    
    print("\n🔍 Listing Available Models:")
    available_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"   - {m.name}")
                available_models.append(m.name)
    except Exception as e:
        print(f"❌ Error listing models: {e}")

    if not available_models:
        print("❌ No models found! Check your API key permissions.")
        exit(1)

    # Pick a model
    model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
    print(f"\n🚀 Attempting to use model: {model_name}")

    model = genai.GenerativeModel(model_name)
    
    print("📨 Sending test message...")
    response = model.generate_content("Hello, are you working?")
    
    print(f"\n✅ SUCCESS! Response: {response.text}")

except Exception as e:
    print(f"\n❌ FAILURE: {e}")
    if "429" in str(e):
        print("\n⚠️ DIAGNOSIS: QUOTA EXCEEDED. You have hit the rate limit.")
        print("   Solution: Wait a few minutes or use a different API key.")
    elif "404" in str(e):
        print("\n⚠️ DIAGNOSIS: MODEL NOT FOUND.")
    else:
        print("\n⚠️ DIAGNOSIS: Unknown error.")
