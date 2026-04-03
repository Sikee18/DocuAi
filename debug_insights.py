import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re
import fitz

load_dotenv()

# Setup Gemini - Same as rag.py
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    genai.configure(api_key=gemini_key)
    gemini_model = genai.GenerativeModel("gemini-pro")
else:
    print("❌ No Gemini API key found")
    exit()

DOCUMENT_PATH = os.path.join(os.getcwd(), "documents")

def debug_extract():
    available_files = [f for f in os.listdir(DOCUMENT_PATH) if f.lower().endswith(('.pdf', '.txt'))]
    if not available_files:
        print("❌ No documents found")
        return

    print(f"📄 Found files: {available_files}")
    doc_summaries = []
    for f in available_files:
        file_path = os.path.join(DOCUMENT_PATH, f)
        text_sample = ""
        try:
            if f.lower().endswith('.pdf'):
                with fitz.open(file_path) as doc:
                    num_pages = len(doc)
                    pages_to_read = sorted(list(set([0, num_pages // 2, num_pages - 1])))
                    for p_num in pages_to_read:
                        if p_num < num_pages:
                            text_sample += f"--- Page {p_num+1} ---\n"
                            text_sample += doc[p_num].get_text()[:3000] + "\n"
            doc_summaries.append(f"DOCUMENT NAME: {f}\nCONTENT SAMPLE:\n{text_sample}\n")
        except Exception as e:
            print(f"❌ Error reading {f}: {e}")

    combined_context = "\n".join(doc_summaries)
    
    prompt = f"""
    You are an Expert Strategic Analyst.
    Identity trends and statistical data.
    JSON SCHEMA:
    {{
        "chart_type": "pie",
        "title": "Strategic Report",
        "labels": ["Segment A", "Segment B"],
        "values": [50, 50],
        "explanation": "Test...",
        "executive_summary": "Test overview...",
        "key_takeaways": ["Point 1"],
        "key_concepts": ["Concept A"],
        "comparison_analysis": ""
    }}
    Rules: Return JSON only.
    DATASET:
    {combined_context[:10000]}
    """

    print("🤖 Calling Gemini-Pro...")
    try:
        response = gemini_model.generate_content(prompt)
        raw_text = response.text.strip()
        print("✅ Received Response")

        json_match = re.search(r'(\{.*\})', raw_text, re.DOTALL)
        if json_match:
            clean_json = json_match.group(1)
            # Standard cleanup
            if "```json" in clean_json:
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_json:
                clean_json = clean_json.split("```")[1].split("```")[0].strip()
            
            data = json.loads(clean_json)
            print("✅ JSON Parsed Successfully")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ No JSON Match Found. Raw response: {raw_text[:200]}")
    except Exception as e:
        print(f"❌ Gemini-Pro Interaction Failed: {e}")

if __name__ == "__main__":
    debug_extract()
