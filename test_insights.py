import os
from DOCU_AI.backend.rag import extract_insights
from dotenv import load_dotenv

load_dotenv()

def test_insights():
    print("🚀 Testing Document Insights Extraction...")
    data, _ = extract_insights()
    
    if "error" in data:
        print(f"❌ Error: {data['error']}")
    else:
        print(f"✅ Success! Chart Type: {data.get('chart_type')}")
        print(f"Title: {data.get('title')}")
        print(f"Labels: {data.get('labels')}")
        print(f"Values: {data.get('values')}")
        print(f"Explanation: {data.get('explanation')}")

if __name__ == "__main__":
    test_insights()
