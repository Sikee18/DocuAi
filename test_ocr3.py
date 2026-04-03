import os
import fitz
import base64
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
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        img_bytes = pix.tobytes("jpeg")
        encoded_string = base64.b64encode(img_bytes).decode('utf-8')
        payload = {
            'base64Image': 'data:image/jpeg;base64,' + encoded_string,
            'language': 'tam',
            'isOverlayRequired': False
        }
        response = requests.post("https://api.ocr.space/parse/image", data=payload, headers={'apikey': 'helloworld'})
        print(json.dumps(response.json(), indent=2))
