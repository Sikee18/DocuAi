import reflex as rx
from DOCU_AI.components.navbar import navbar
from DOCU_AI.components.footer import footer

def about():
    return rx.box(
        navbar(),

        rx.box(
            rx.vstack(
                rx.heading("🧠 About DocuAI", size="7"),

                rx.text(
                    "DocuAI is an AI-powered document intelligence system that allows users "
                    "to upload and interact with documents using natural language queries. "
                    "It uses Retrieval-Augmented Generation (RAG) to provide accurate, context-aware answers."
                ),

                rx.heading("⚙️ Key Features", size="5"),
                rx.text("• Upload and process PDF, TXT, CSV files"),
                rx.text("• Ask questions in natural language"),
                rx.text("• Context-aware AI responses"),
                rx.text("• Confidence score and source tracking"),
                rx.text("• Chat history for conversation flow"),

                rx.heading("🏗️ System Architecture", size="5"),
                rx.text("1. Document Upload"),
                rx.text("2. Text Extraction & Processing"),
                rx.text("3. Chunking using text splitters"),
                rx.text("4. Embedding generation"),
                rx.text("5. Vector storage (ChromaDB)"),
                rx.text("6. Similarity-based retrieval"),
                rx.text("7. Answer generation using LLM"),

                rx.heading("🧪 Technologies Used", size="5"),
                rx.text("• Frontend: Reflex"),
                rx.text("• Backend: Python"),
                rx.text("• LLM: Groq (LLaMA 3.1)"),
                rx.text("• Embeddings: Sentence Transformers"),
                rx.text("• Vector Database: ChromaDB"),
                rx.text("• Framework: LangChain"),

                rx.heading("🎯 Use Cases", size="5"),
                rx.text("• Academic research assistance"),
                rx.text("• Resume analysis"),
                rx.text("• Business document insights"),
                rx.text("• CSV data understanding"),
                rx.text("• Document summarization"),

                rx.heading("👩‍💻 Developer", size="5"),
                rx.text(
                    "Developed as a Final Year Project focusing on AI-powered document "
                    "understanding and intelligent retrieval systems."
                ),

                spacing="4",
                align="start",
            ),
            padding="30px",
        ),

        
    )