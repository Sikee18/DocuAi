import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import json
import re

load_dotenv()

# Setup Groq
groq_key = os.getenv("GROQ_API_KEY")
if groq_key:
    llm = ChatGroq(
        model='llama-3.3-70b-versatile',
        temperature=0.1,
        api_key=groq_key
    )
else:
    print("❌ No Groq API key found")
    exit()

def test_groq_insights():
    prompt = """
    You are an Expert Strategic Analyst.
    Return ONLY a JSON object exactly like this:
    {
        "chart_type": "bar",
        "title": "Groq Intelligence Test",
        "labels": ["Efficiency", "Accuracy", "Speed"],
        "values": [95, 98, 99],
        "explanation": "Groq is extremely stable.",
        "executive_summary": "System confirms Groq bridge is operational.",
        "key_takeaways": ["Fast", "Reliable"],
        "key_concepts": ["LLM"],
        "comparison_analysis": "Groq outperforms legacy Gemini connectivity in this environment."
    }
    """
    
    print("🤖 Calling Groq...")
    try:
        response = llm.invoke(prompt)
        raw_text = response.content.strip()
        print("✅ Received Response")
        
        json_match = re.search(r'(\{.*\})', raw_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1))
            print("✅ JSON Parsed Successfully")
            print(json.dumps(data, indent=2))
        else:
            print("❌ No JSON Found")
    except Exception as e:
        print(f"❌ Groq Failed: {e}")

if __name__ == "__main__":
    test_groq_insights()
