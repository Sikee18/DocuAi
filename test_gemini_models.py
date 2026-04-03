import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Setup Gemini
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    genai.configure(api_key=gemini_key)
else:
    print("❌ No Gemini API key found")
    exit()

models_to_try = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro"
]

for m_name in models_to_try:
    print(f"\n--- Testing {m_name} ---")
    try:
        model = genai.GenerativeModel(m_name)
        response = model.generate_content("Say hello in one word.")
        print(f"✅ {m_name} worked: {response.text.strip()}")
    except Exception as e:
        print(f"❌ {m_name} failed: {e}")
