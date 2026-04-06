import os
import google.generativeai as genai
from langdetect import detect
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# -------------------------------
# Initialize Models
# -------------------------------
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    genai.configure(api_key=gemini_key)
    gemini_model = genai.GenerativeModel("gemini-pro")
else:
    gemini_model = None

try:
    vision_model = genai.GenerativeModel("gemini-1.1-pro-vision-latest")
except:
    vision_model = None

# Build-safe initialization: Use dummy key if actual key is missing during Docker build phase.
groq_key = os.getenv("GROQ_API_KEY") or "gsk_build_time_placeholder"

# Normal chat model (8b)
llm = ChatGroq(
    model='llama-3.1-8b-instant',
    temperature=0.7,
    api_key=groq_key
)

# Heavy-duty intelligence model (70b) specifically for insights
llm_insights = ChatGroq(
    model='llama-3.3-70b-versatile',
    temperature=0.1, # Keep it strictly logical for JSON
    api_key=groq_key
)


# -------------------------------
# Global Configuration
# -------------------------------
vectorstore = None
retriever = None
DOCUMENT_PATH = os.path.join(os.getcwd(), "documents")
os.makedirs(DOCUMENT_PATH, exist_ok=True)

# -------------------------------
# Utilities
# -------------------------------
def clean_json_text(text: str) -> str:
    """Robust utility to clean and fix AI-generated JSON strings."""
    import re
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if not match: return text
    json_str = match.group(1)
    json_str = re.sub(r",\s*([\]}])", r"\1", json_str)
    return json_str

def process_image_with_vision(file_path_or_bytes):
    if not vision_model: return ""
    try:
        import PIL.Image
        import io
        if isinstance(file_path_or_bytes, str):
            img = PIL.Image.open(file_path_or_bytes)
        else:
            img = PIL.Image.open(io.BytesIO(file_path_or_bytes))
        response = vision_model.generate_content(["Transcribe the text from this image.", img])
        return response.text.strip()
    except: return ""

def format_docs(docs):
    context = "\n".join([doc.page_content for doc in docs])
    sources = list(set([doc.metadata.get("source", "unknown") for doc in docs]))
    return context, sources

# -------------------------------
# Core RAG Logic
# -------------------------------
def build_vectorstore():
    global retriever, vectorstore
    print("🔄 Rebuilding Vector DB...")
    from langchain_community.document_loaders import DirectoryLoader, TextLoader, Docx2txtLoader, CSVLoader
    from langchain_core.documents import Document
    import fitz

    docs = []
    # PDF Loader with OCR
    for f in os.listdir(DOCUMENT_PATH):
        if f.lower().endswith('.pdf'):
            try:
                file_path = os.path.join(DOCUMENT_PATH, f)
                with fitz.open(file_path) as pd:
                    for i, page in enumerate(pd):
                        text = page.get_text().strip()
                        if len(text) < 100 or "CamScanner" in text:
                            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                            text = process_image_with_vision(pix.tobytes("png")) or text
                        if text.strip():
                            docs.append(Document(page_content=text.strip(), metadata={"source": file_path, "page": i}))
            except: pass
    
    # Other loaders
    for loader_cls, glob in [(TextLoader, "*.txt"), (Docx2txtLoader, "*.docx"), (CSVLoader, "*.csv")]:
        try:
            loader = DirectoryLoader(path=DOCUMENT_PATH, glob=glob, loader_cls=loader_cls)
            docs.extend(list(loader.lazy_load()))
        except: pass

    if not docs:
        retriever = None
        return

    # Split & Embed (Switched to Gemini API explicitly to save 300MB+ RAM during Render's strict 512MB free tier Memory Caps!)
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma
    from langchain_core.embeddings import Embeddings

    class GeminiEmbeddings(Embeddings):
        def embed_documents(self, texts: list[str]) -> list[list[float]]:
            res = genai.embed_content(model="models/embedding-001", content=texts)
            return res.get('embedding', []) if isinstance(res.get('embedding', []), list) else [res.get('embedding', [])]
        def embed_query(self, text: str) -> list[float]:
            res = genai.embed_content(model="models/embedding-001", content=text)
            return res.get('embedding', [])

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=30)
    splitted_docs = splitter.split_documents(docs)
    
    embedding_model = GeminiEmbeddings()
    vectorstore = Chroma.from_documents(documents=splitted_docs, embedding=embedding_model)
    retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 3})

def corrective_rag(query, preferred_language="English"):
    if retriever is None: return "Upload files first.", []
    retrieved_docs = retriever.invoke(query)
    context, sources = format_docs(retrieved_docs)
    
    prompt = f"Answer strictly from context in {preferred_language}.\nContext: {context}\nQuestion: {query}"
    answer = llm.invoke(prompt)
    return answer.content, sources

def get_answer(query: str, preferred_language: str = "English"):
    global retriever
    if retriever is None: build_vectorstore()
    if retriever is None: return "Upload files first.", []
    return corrective_rag(query, preferred_language)

# -------------------------------
# Insights Visualization (REBUILT FOR STABILITY)
# -------------------------------
def extract_insights(target_files: list[str] = None):
    available_files = [f for f in os.listdir(DOCUMENT_PATH) if f.lower().endswith(('.pdf', '.txt'))]
    files_to_process = target_files if target_files else available_files
    if not files_to_process: return {"error": "No documents found."}, []

    doc_summaries = []
    for f in files_to_process:
        if f not in available_files: continue
        file_path = os.path.join(DOCUMENT_PATH, f)
        text_sample = ""
        try:
            import fitz
            with fitz.open(file_path) as doc:
                num_pages = len(doc)
                pages = sorted(list(set([0, num_pages // 2, num_pages - 1])))
                for p in pages:
                    if p < num_pages: text_sample += doc[p].get_text()[:3000] + "\n"
            doc_summaries.append(f"FILE: {f}\nCONTENT: {text_sample}")
        except: continue

    combined_context = "\n".join(doc_summaries)
    prompt = f"""
    Expert Strategic Analyst: Analyze documents and return JSON. 
    IMPORTANT: If the document contains NO numerical statistics, you MUST generate "Mention Frequency" or "Impact Score" for the top 5 key themes/concepts to use as numerical values.
    
    SCHEMA: {{
        "chart_type": "pie" | "bar",
        "title": "Strategic Report",
        "labels": ["Concept A", "Concept B", "Concept C", "Concept D", "Concept E"],
        "values": [45, 30, 15, 5, 5],
        "explanation": "Brief context...",
        "executive_summary": "Detailed summary...",
        "key_takeaways": ["Point 1", "Point 2", "Point 3"],
        "key_concepts": ["Concept 1", "Concept 2"],
        "comparison_analysis": ""
    }}
    Rules: Strictly JSON only. No trailing commas.
    DATA: {combined_context[:15000]}
    """

    try:
        import json
        # Using the 70B model for 100% reliable JSON
        response = llm_insights.invoke(prompt)
        raw_text = response.content.strip()
        
        clean_json = clean_json_text(raw_text)
        
        try:
            data = json.loads(clean_json)
            # Ensure fields exist
            if not data.get("labels"): data["labels"] = ["Theme A", "Theme B", "Theme C"]
            if not data.get("values"): data["values"] = [40, 40, 20]
            return data, []
        except:
            import re
            match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                if not data.get("labels"): data["labels"] = ["Theme A", "Theme B", "Theme C"]
                if not data.get("values"): data["values"] = [40, 40, 20]
                return data, []
            raise ValueError("No valid JSON found")
            
    except Exception as e:
        print(f"🚨 Insights Error (70B): {e}")
        return {"error": f"Insights analysis failed. Please try a cleaner sample."}, []


