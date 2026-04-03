import os
import fitz
import requests

DOCUMENT_PATH = "C:\\Users\\rathu\\Downloads\\RAG-APPLICATION-main\\RAG-APPLICATION-main\\documents"
file_path = os.path.join(DOCUMENT_PATH, "Part I Tamil.pdf")

doc = fitz.open(file_path)
page = doc[0]
pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
pix.save("temp.jpg")

with open("temp.jpg", "rb") as f:
    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"file": f},
        data={"apikey": "helloworld", "language": "tam"}
    )

print(response.json())
