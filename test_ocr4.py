import os
import fitz
import requests
import json

DOCUMENT_PATH = "C:\\Users\\rathu\\Downloads\\RAG-APPLICATION-main\\RAG-APPLICATION-main\\documents"

docs = [f for f in os.listdir(DOCUMENT_PATH) if f.lower().endswith('.pdf')]
if not docs:
    print("No PDFs found.")
else:
    file_path = os.path.join(DOCUMENT_PATH, docs[0])
    with fitz.open(file_path) as pd:
        page = pd[0]
        # Test default matrix
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("jpeg")
        
        payload = {
            'language': 'tam',
            'isOverlayRequired': False
        }
        
        # Send raw bytes instead of base64!
        files = {
            'file': ('image.jpg', img_bytes, 'image/jpeg')
        }
        
        response = requests.post("https://api.ocr.space/parse/image", data=payload, files=files, headers={'apikey': 'helloworld'})
        print(json.dumps(response.json(), indent=2))
