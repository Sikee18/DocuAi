import os
import fitz
import base64
import requests

DOCUMENT_PATH = "C:\\Users\\rathu\\Downloads\\RAG-APPLICATION-main\\RAG-APPLICATION-main\\documents"

docs = os.listdir(DOCUMENT_PATH)
pdf_files = [f for f in docs if f.lower().endswith('.pdf')]
if not pdf_files:
    print("No PDFs")
else:
    file_path = os.path.join(DOCUMENT_PATH, pdf_files[0])
    print(f"Testing PDF: {pdf_files[0]}")
    with fitz.open(file_path) as pd:
        page = pd[0]
        
        # Test 1x Matrix
        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
        # Compress it heavily for API
        img_bytes = pix.tobytes("jpeg")
        print(f"Image 1x Size: {len(img_bytes) / 1024:.2f} KB")
        
        encoded_string = base64.b64encode(img_bytes).decode('utf-8')
        payload = {'base64Image': 'data:image/jpeg;base64,' + encoded_string, 'language': 'tam'}
        response = requests.post("https://api.ocr.space/parse/image", data=payload, headers={'apikey': 'helloworld'}).json()
        print("API Response:", response)
