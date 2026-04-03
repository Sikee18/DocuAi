import os
import sys
from dotenv import load_dotenv
import requests

load_dotenv("c:/Users/rathu/Downloads/RAG-APPLICATION-main/RAG-APPLICATION-main/.env")
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("No API Key")
    sys.exit(1)

url = "https://api.groq.com/openai/v1/models"
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
try:
    response = requests.get(url, headers=headers)
    models = response.json().get('data', [])
    for m in models:
        m_id = m.get('id', '')
        if 'vision' in m_id.lower() or 'llama' in m_id.lower():
            print(f"Model ID: {m_id}")
except Exception as e:
    print(f"Error: {e}")
