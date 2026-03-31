    
# -------------------------------
# Imports
# -------------------------------

# from langchain_huggingface import HuggingFaceEmbeddings # Removed to stay under 4GB limit
from langchain_groq import ChatGroq
from langchain_community.embeddings import FakeEmbeddings
from dotenv import load_dotenv

import os

load_dotenv()

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

# -------------------------------
# GLOBAL VARIABLES (IMPORTANT)
# -------------------------------
vectorstore = None
retriever = None

#DOCUMENT_PATH = "RAG_PROJECT/documents"   # ✅ fixed spelling
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCUMENT_PATH = os.path.join(BASE_DIR, "documents")


def build_vectorstore():
    global retriever, vectorstore

    print("🔄 Rebuilding Vector DB...")
    from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma
    

    pdf_loader = DirectoryLoader(
        path=DOCUMENT_PATH,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )

    txt_loader = DirectoryLoader(
        path=DOCUMENT_PATH,
        glob="*.txt",
        loader_cls=TextLoader
    )
    print("Loading PDF...")
    pdf_docs = list(pdf_loader.lazy_load())

    print("Loading TXTs....")
    txt_docs = list(txt_loader.lazy_load())

    print("PDF count:", len(pdf_docs))
    print("TXT count:", len(txt_docs))

    docs = pdf_docs + txt_docs

    if not docs:
        print("⚠️ No documents found!")
        retriever=None
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30
    )

    splitted_docs = splitter.split_documents(docs)
    print("Creating vectorestore...")
    #embedding_model =FakeEmbeddings(size=384)
    from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
    embedding_model = FastEmbedEmbeddings(
        model_name="BAAI/bge-small-en-v1.5"
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
def corrective_rag(query):
    global retriever

    if retriever is None:
        return "No documents available. Please upload files first.", []

    # -------------------------------
    # Conversational Bypass
    # -------------------------------
    bypass_prompt = f"""
    Is the following user input a simple greeting, a compliment, or a casual conversational remark that does NOT require looking up factual intelligence from a document?
    (Examples: 'hello', 'hi', 'hey', 'who are you', 'how are you', 'thanks')
    
    User Input: "{query}"
    
    Answer STRICTLY with 'YES' or 'NO'. Do not provide any other text.
    """
    
    is_conversational = llm.invoke(bypass_prompt).content.strip().upper()
    if "YES" in is_conversational:
        print("🤖 Conversational Bypass Triggered")
        chat_prompt = f"The user said: '{query}'. Respond to them politely as an intelligent AI assistant. If they are saying hello, warmly greet them and mention you are ready to answer questions based on their uploaded documents. Keep the response concise and friendly."
        response = llm.invoke(chat_prompt).content.strip()
        return response, []

    print("\n🔍 Initial Retrieval")
    retrieved_docs = retriever.invoke(query)
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
    Answer the question using ONLY the context below.

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
def get_answer(query: str):
    global retriever
    # print("Retriver:",retriever)  

    if retriever is None:
        build_vectorstore() 
    print("Retriver after build:",retriever)   
    if retriever is None:
        return "No documents found, Please upload documents first.",[]   
    answer, sources = corrective_rag(query)
    return answer, sources
    #return corrective_rag(query)


# -------------------------------
# INITIAL LOAD (RUN ON START)
# -------------------------------
  