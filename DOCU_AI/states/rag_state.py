import reflex as rx
from typing import List
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from DOCU_AI.backend.rag import get_answer
from pydantic import BaseModel
import os

# ✅ Create proper data model
class ChatItem(BaseModel):
    question: str
    answer: str
    sources: str



class ChatState(rx.State):
    question: str = ""
    history: List[ChatItem] = []
    is_loading: bool = False   # ✅ ADD THIS

    def handle_submit(self, form_data: dict):
        self.question = form_data.get("chat_input", "")
        self.ask_question()

    def ask_question(self):
        if not self.question.strip():
            return

        self.is_loading = True   # 🔥 START LOADING

        answer, sources = get_answer(self.question)

        if isinstance(sources, list):
            sources = ", ".join([os.path.basename(s) for s in sources])
        else:
            sources = os.path.basename(sources)    

        new_item = ChatItem(
            question=self.question,
            answer=answer,
            sources=sources
        )

        self.history = self.history + [new_item]

        self.question = ""
        self.is_loading = False   # 🔥 STOP LOADING

    def clear_history(self):##
       self.history = []    

    def download_chat(self):
        import time
        import os

        # Create a unique filename to prevent browser caching
        timestamp = int(time.time())
        filename = f"chat_history_{timestamp}.pdf"
        file_path = f"assets/{filename}"

        # Clean up any existing old chat history files in assets to keep it tidy
        if os.path.exists("assets"):
            for f in os.listdir("assets"):
                if f.startswith("chat_history_") and f.endswith(".pdf"):
                    try:
                        os.remove(os.path.join("assets", f))
                    except Exception:
                        pass

        doc = SimpleDocTemplate(file_path)
        styles = getSampleStyleSheet()

        elements = []

        # Loop through chat history
        for item in self.history:
            elements.append(Paragraph(f"<b>Question:</b> {item.question}", styles["Normal"]))
            elements.append(Spacer(1, 10))

            elements.append(Paragraph(f"<b>Answer:</b> {item.answer}", styles["Normal"]))
            elements.append(Spacer(1, 10))

            elements.append(Paragraph(f"<b>Sources:</b> {item.sources}", styles["Normal"]))
            elements.append(Spacer(1, 20))

        doc.build(elements)

        return rx.download(f"/{filename}")   # 🔥 Fresh download every time