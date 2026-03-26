import sys
import docx

def read_docx(file_path):
    try:
        doc = docx.Document(file_path)
        full_text = []
        for p in doc.paragraphs:
            if p.text.strip():
                full_text.append(p.text)
        with open("extracted_doc.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(full_text))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_docx(sys.argv[1])
