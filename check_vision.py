import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

models = client.models.list()
for model in models.data:
    if "vision" in model.id.lower():
        print(f"VISION MODEL FOUND: {model.id}")
    else:
         print(f"Other model: {model.id}")
