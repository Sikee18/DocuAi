import os
import fitz
import google.generativeai as genai
from dotenv import load_dotenv
import PIL.Image
import io

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

DOCUMENT_PATH = "C:\\Users\\rathu\\Downloads\\RAG-APPLICATION-main\\RAG-APPLICATION-main\\documents"

def test_gemini_ocr():
    docs = [f for f in os.listdir(DOCUMENT_PATH) if f.lower().endswith('.pdf')]
    if not docs:
        print("No PDF found in documents folder.")
        return

    file_path = os.path.join(DOCUMENT_PATH, docs[0])
    print(f"Testing Gemini OCR on: {docs[0]}")
    
    with fitz.open(file_path) as pd:
        page = pd[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_bytes = pix.tobytes("png")
        
        img = PIL.Image.open(io.BytesIO(img_bytes))
        prompt = "Extract all text from this image exactly as it appears. If it is in Tamil, preserve the Tamil script accurately."
        
        print("Sending to Gemini...")
        response = model.generate_content([prompt, img])
        print("\n--- GEMINI OUTPUT ---")
        print(response.text)
        print("----------------------")

if __name__ == "__main__":
    test_gemini_ocr()
