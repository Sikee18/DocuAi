    
# -------------------------------
# Imports
# -------------------------------

# from langchain_huggingface import HuggingFaceEmbeddings # Removed to stay under 4GB limit
from langchain_groq import ChatGroq
from langchain_community.embeddings import FakeEmbeddings
from dotenv import load_dotenv

import os
import google.generativeai as genai
from langdetect import detect

load_dotenv()

# -------------------------------
# Initialize Gemini (Vision/OCR)
# -------------------------------
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    genai.configure(api_key=gemini_key)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    gemini_model = None

# -------------------------------
# Initialize LLM
# -------------------------------
# Build-safe initialization: Use dummy key if actual key is missing during Docker build phase.
groq_key = os.getenv("GROQ_API_KEY") or "gsk_build_time_placeholder"
llm = ChatGroq(
    model='llama-3.1-8b-instant',
    temperature=0.7,
    api_key=groq_key
)

def process_image_with_vision(file_path_or_bytes):
    """Uses Gemini 1.5 Flash for advanced OCR and Vision analysis."""
    if not gemini_model:
        print("⚠️ Gemini API Key missing. Skipping Vision OCR.")
        return ""

    try:
        import PIL.Image
        import io

        if isinstance(file_path_or_bytes, str):
            img = PIL.Image.open(file_path_or_bytes)
        else:
            img = PIL.Image.open(io.BytesIO(file_path_or_bytes))

        prompt = "Extract all text from this image exactly as it appears. If it is in Tamil, preserve the Tamil script accurately. If it is a scanned document, transribe all visible text. Only return the transcribed text, nothing else."
        
        response = gemini_model.generate_content([prompt, img])
        return response.text.strip()
            
    except Exception as e:
        print(f"Gemini Vision Failed: {e}")
        
    return ""

# -------------------------------
# GLOBAL VARIABLES (IMPORTANT)
# -------------------------------
vectorstore = None
retriever = None

# Hardcode relative to execution dir just like upload.py
DOCUMENT_PATH = os.path.join(os.getcwd(), "documents")
os.makedirs(DOCUMENT_PATH, exist_ok=True)


def build_vectorstore():
    global retriever, vectorstore

    print("🔄 Rebuilding Vector DB...")
    from langchain_community.document_loaders import DirectoryLoader, TextLoader, Docx2txtLoader, CSVLoader
    from langchain_core.documents import Document

    txt_loader = DirectoryLoader(path=DOCUMENT_PATH, glob="*.txt", loader_cls=TextLoader)
    docx_loader = DirectoryLoader(path=DOCUMENT_PATH, glob="*.docx", loader_cls=Docx2txtLoader)
    csv_loader = DirectoryLoader(path=DOCUMENT_PATH, glob="*.csv", loader_cls=CSVLoader)

    print("Loading PDFs with precision OCR (PyMuPDF)...")
    import fitz
    pdf_docs = []
    for f in os.listdir(DOCUMENT_PATH):
        if f.lower().endswith('.pdf'):
            try:
                file_path = os.path.join(DOCUMENT_PATH, f)
                with fitz.open(file_path) as pd:
                    for i, page in enumerate(pd):
                        text = page.get_text().strip()
                        # If page is empty or just watermark, run Gemini Vision for deep OCR
                        if len(text) < 100 or "CamScanner" in text:
                            try:
                                print(f"🔍 Deep Scanning PDF Page {i} with Gemini...")
                                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                                img_bytes = pix.tobytes("png")
                                extracted_text = process_image_with_vision(img_bytes)
                                if extracted_text:
                                    text = extracted_text # Replace or append depending on need. Here we replace for cleaner results
                            except Exception as e:
                                print(f"Gemini OCR failed for PDF page {i}: {e}")
                        
                        if text.strip():
                            pdf_docs.append(Document(page_content=text.strip(), metadata={"source": file_path, "page": i}))
            except Exception as e:
                print(f"Failed to process PDF {f}: {e}")
    
    print("Loading TXTs...")
    txt_docs = list(txt_loader.lazy_load())

    print("Loading DOCXs & CSVs...")
    docx_docs = list(docx_loader.lazy_load())
    csv_docs = list(csv_loader.lazy_load())
    
    image_docs = []
    print("Loading Images using Fast Offline OCR...")
    for f in os.listdir(DOCUMENT_PATH):
        if f.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                img_path = os.path.join(DOCUMENT_PATH, f)
                extracted_text = process_image_with_vision(img_path)
                if extracted_text:
                    image_docs.append(Document(page_content=extracted_text, metadata={"source": img_path}))
            except Exception as e:
                print(f"Failed to process image {f}: {e}")

    docs = pdf_docs + txt_docs + docx_docs + csv_docs + image_docs

    if not docs:
        print("⚠️ No documents found!")
        retriever=None
        return

    # Detect language for each document before splitting
    for doc in docs:
        try:
            # Use the first 500 characters to detect language
            lang = detect(doc.page_content[:500])
        except Exception:
            lang = "unknown"
        doc.metadata["detected_language"] = lang

    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=30
    )

    splitted_docs = splitter.split_documents(docs)
    
    # Add chunk index metadata
    for i, chunk in enumerate(splitted_docs):
        chunk.metadata["chunk_index"] = i
        
    print("Creating vectorestore...")
    #embedding_model =FakeEmbeddings()
    from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
    embedding_model = FastEmbedEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    vectorstore = Chroma.from_documents(
        documents=splitted_docs,
        embedding=embedding_model,
        #persist_directory="./chroma_db"
    )

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 3, "lambda_mult": 0.7}
    )

    print("✅ Vector DB Ready!")
    print("FINAL RETRIVEVER:",retriever)


# -------------------------------
# Utility: Format Docs
# -------------------------------
def format_docs(docs):
    context = "\n".join([doc.page_content for doc in docs])
    sources = list(set([doc.metadata.get("source", "unknown") for doc in docs]))
    return context, sources


# -------------------------------
# Corrective RAG
# -------------------------------
def corrective_rag(query, preferred_language="English"):
    global retriever

    if retriever is None:
        return "No documents available. Please upload files first.", []

    # -------------------------------
    # Linguistic Pivot (Multilingual Optimization)
    # -------------------------------
    try:
        user_lang = detect(query)
    except:
        user_lang = "en"
    
    internal_query = query
    if user_lang != "en":
        print(f"🌍 Detected {user_lang}. Translating to English for optimal retrieval...")
        translation_prompt = f"""
        Translate the following user question to clear, technical English for retrieval from a vector database. 
        Important: The user may be using phonetic transliteration (e.g., Tanglish, Hinglish, or Romanized script for other languages). 
        Identify the core intent and translate it to formal English.
        Only return the English translation: '{query}'
        """
        internal_query = llm.invoke(translation_prompt).content.strip()
        print(f"🔍 Internal English Query: {internal_query}")

    # -------------------------------
    # Conversational Bypass
    # -------------------------------
    bypass_prompt = f"""
    Is the following user input a simple greeting, a compliment, or a casual conversational remark that does NOT require looking up factual intelligence from a document?
    (Examples: 'hello', 'hi', 'hey', 'who are you', 'how are you', 'thanks')
    
    User Input: "{internal_query}"
    
    Answer STRICTLY with 'YES' or 'NO'. Do not provide any other text.
    """
    
    is_conversational = llm.invoke(bypass_prompt).content.strip().upper()
    if "YES" in is_conversational:
        print("🤖 Conversational Bypass Triggered")
        chat_prompt = f"The user said: '{query}'. Respond to them politely as an intelligent AI assistant in {preferred_language}. If they are saying hello, warmly greet them and mention you are ready to answer questions based on their uploaded documents. Keep the response concise and friendly."
        response = llm.invoke(chat_prompt).content.strip()
        return response, []

    print("\n🔍 Initial Retrieval")
    retrieved_docs = retriever.invoke(internal_query)
    context, sources = format_docs(retrieved_docs)

    # -------------------------------
    # Relevance Check
    # -------------------------------
    evaluation_prompt = f"""
    Query: {query}

    Retrieved Context:
    {context}

    Are these documents relevant enough to answer the query?
    Respond strictly with YES or NO.
    """

    evaluation = llm.invoke(evaluation_prompt).content.strip()
    print("Relevance Check:", evaluation)

    # -------------------------------
    # Query Rewrite if needed
    # -------------------------------
    if "NO" in evaluation.upper():

        print("✏️ Rewriting Query...")

        rewrite_prompt = f"""
        The query '{query}' did not retrieve relevant documents.
        Rewrite it to improve retrieval quality.
        Only return the improved query.
        """

        improved_query = llm.invoke(rewrite_prompt).content.strip()
        print("Improved Query:", improved_query)

        retrieved_docs = retriever.invoke(improved_query)
        context, sources = format_docs(retrieved_docs)

    # -------------------------------
    # Final Answer
    # -------------------------------
    final_prompt = f"""
    Answer the following question strictly using the provided document context. Do not invent information. 
    Respond in the following language: {preferred_language}.

    Context:
    {context}

    Question: {query}

    Also mention the sources used at the end.
    """

    answer = llm.invoke(final_prompt)

    return answer.content, sources


# -------------------------------
# Public Function (USED BY UI)
# -------------------------------
def get_answer(query: str, preferred_language: str = "English"):
    global retriever
    # print("Retriver:",retriever)  

    if retriever is None:
        build_vectorstore() 
    print("Retriver after build:",retriever)   
    if retriever is None:
        return "No documents found, Please upload documents first.",[]   
    answer, sources = corrective_rag(query, preferred_language)
    return answer, sources

# -------------------------------
# Document Insight Visualization
# -------------------------------
def extract_insights(target_files: list[str] = None):
    """Analyzes documents and returns a synthesized JSON report. 
    If target_files is provided, focus only on those. If None, analyze all."""
    if not gemini_model:
        return {"error": "Gemini API Key missing"}, []

    doc_summaries = []
    # If target_files is provided, use only those. Else, use all documents in the folder.
    available_files = [f for f in os.listdir(DOCUMENT_PATH) if f.lower().endswith(('.pdf', '.txt'))]
    files_to_process = target_files if target_files else available_files
    
    if not files_to_process:
        return {"error": "No documents found to analyze."}, []

    print(f"📊 Generating Insights for {len(files_to_process)} documents (Mode: {'Single' if len(files_to_process)==1 else 'Cross-Doc'})...")

    for f in files_to_process:
        if f not in available_files: continue
        file_path = os.path.join(DOCUMENT_PATH, f)
        text_sample = ""
        try:
            if f.lower().endswith('.pdf'):
                import fitz
                with fitz.open(file_path) as doc:
                    num_pages = len(doc)
                    pages_to_read = sorted(list(set([0, num_pages // 2, num_pages - 1])))
                    for p_num in pages_to_read:
                        if p_num < num_pages:
                            text_sample += f"--- Page {p_num+1} ---\n"
                            text_sample += doc[p_num].get_text()[:3000] + "\n"
            elif f.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as tf:
                    content = tf.read()
                    length = len(content)
                    if length > 9000:
                        text_sample = content[:3000] + "\n[...]\n" + content[length//2:length//2+3000] + "\n[...]\n" + content[-3000:]
                    else:
                        text_sample = content
            doc_summaries.append(f"DOCUMENT NAME: {f}\nCONTENT SAMPLE:\n{text_sample}\n")
        except: continue

    combined_context = "\n".join(doc_summaries)
    is_cross_doc = len(files_to_process) > 1
    
    prompt = f"""
    You are an Expert Strategic Analyst.
    {'You are analyzing a COLLECTION of ' + str(len(files_to_process)) + ' documents.' if is_cross_doc else 'You are performing a DEEP FOCUS analysis on a SINGLE document.'}
    
    TASKS:
    1. Identify trends, statistical data, and conceptual relationships.
    2. { 'COMPARE AND CONTRAST: Identify contradictions, synergies, or trends between these different files.' if is_cross_doc else 'DEEP EXTRACTION: Extract detailed metrics and strategic pillars from this specific file.' }
    
    JSON SCHEMA:
    {{
        "chart_type": "pie" | "bar" | "line",
        "title": "Strategic Report: [Subject]",
        "labels": ["Label1", "Label2", "Label3", ...],
        "values": [Val1, Val2, Val3, ...],
        "explanation": "Context...",
        "executive_summary": "High-level overview...",
        "key_takeaways": ["Takeaway1", "Takeaway2", "Takeaway3"],
        "key_concepts": ["Concept1", "Concept2", "Concept3"],
        "comparison_analysis": "{ 'Detailed comparison text...' if is_cross_doc else '' }"
    }}

    Rules: Return JSON only. Minimum 3 data points. 
    
    DATASET:
    {combined_context[:20000]}
    """
    
    try:
        import json
        response = gemini_model.generate_content(prompt)
        raw_text = response.text.strip()
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_text:
             raw_text = raw_text.split("```")[1].split("```")[0].strip()
            
        insight_data = json.loads(raw_text)
        return insight_data, []
    except Exception as e:
        print(f"Extraction Failed: {e}")
        return {"error": "Context analysis failed. The documents may be too dense or unformatted."}, []


# -------------------------------
# INITIAL LOAD (RUN ON START)
# -------------------------------
  
