import os
import fitz
import base64
import requests

from DOCU_AI.backend.rag import DOCUMENT_PATH

def test_ocr():
    docs = os.listdir(DOCUMENT_PATH)
    pdf_files = [f for f in docs if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in documents.")
        return

    file_path = os.path.join(DOCUMENT_PATH, pdf_files[0])
    print(f"Testing PDF: {pdf_files[0]}")
    
    with fitz.open(file_path) as pd:
        page = pd[0]
        text = page.get_text().strip()
        print(f"Extracted Text length: {len(text)}")
        print(f"Extracted Text: {text[:100]}")
        
        print("Running OCR...")
        # 1.5x resolution for good OCR accuracy without hitting 1MB barrier
        matrix = fitz.Matrix(1.5, 1.5)
        pix = page.get_pixmap(matrix=matrix)
        
        # Jpeg encoding with standard options
        img_bytes = pix.tobytes("jpeg")
        print(f"Image byte size: {len(img_bytes) / 1024:.2f} KB")
        
        encoded_string = base64.b64encode(img_bytes).decode('utf-8')
        payload = {'base64Image': 'data:image/jpeg;base64,' + encoded_string, 'language': 'tam'}
        
        response = requests.post("https://api.ocr.space/parse/image", data=payload, headers={'apikey': 'helloworld'}).json()
        print("OCR API Response:", response)
        
        if not response.get('IsErroredOnProcessing') and response.get('ParsedResults'):
             print("\nParsed Text:")
             print(response['ParsedResults'][0]['ParsedText'])

if __name__ == "__main__":
    test_ocr()
