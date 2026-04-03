import reflex as rx
from typing import List
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from DOCU_AI.backend.rag import get_answer
import os
from langdetect import detect

# ✅ Create proper data model — must be rx.Base for Reflex state serialization
class ChatItem(rx.Base):
    question: str = ""
    answer: str = ""
    sources: str = ""
    question_language: str = ""
    response_language: str = ""



class ChatState(rx.State):
    question: str = ""
    history: List[ChatItem] = []
    is_loading: bool = False
    preferred_language: str = "English"
    chart_ready: bool = False

    def handle_submit(self, form_data: dict):
        question = form_data.get("chat_input", "").strip()
        if not question:
            return
        self.question = question
        yield from self.ask_question()

    def ask_question(self):
        if not self.question.strip():
            return

        self.is_loading = True
        self.chart_ready = False
        yield

        # Check for visualization intent
        viz_keywords = ["visualize", "chart", "graph", "insight", "relationship", "trend"]
        is_viz_request = any(word in self.question.lower() for word in viz_keywords)

        try:
            # Better detection using the actual query
            user_input_lang = detect(self.question)
        except:
            user_input_lang = "unknown"

        if is_viz_request:
            answer = f"I've analyzed your documents for visual intelligence. I've prepared a dedicated dashboard with charts and relationship maps for you. Click the button below or go to the Insights page to view them.\n\n(Translated to {self.preferred_language} for your convenience)"
            sources = "System Intelligence"
        else:
            answer, sources = get_answer(self.question, self.preferred_language)

        if isinstance(sources, list):
            sources = ", ".join([os.path.basename(s) for s in sources])
        else:
            sources = os.path.basename(str(sources))

        new_item = ChatItem(
            question=self.question,
            answer=answer,
            sources=sources,
            question_language=user_input_lang.upper(),
            response_language=self.preferred_language
        )

        self.history = self.history + [new_item]
        
        # If it was a viz request, we can optionally redirect or just stay
        # In this case, providing a link in the message is best.
        
        self.question = ""
        self.is_loading = False

    def clear_history(self):##
       self.history = []    

    def download_chat(self):
        import io
        import base64
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        # Use BytesIO to generate PDF in memory to bypass production static-file caching bugs
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()

        elements = []

        # Loop through chat history
        for item in self.history:
            elements.append(Paragraph(f"<b>Question ({item.question_language}):</b> {item.question}", styles["Normal"]))
            elements.append(Spacer(1, 10))

            elements.append(Paragraph(f"<b>Answer ({item.response_language}):</b> {item.answer}", styles["Normal"]))
            elements.append(Spacer(1, 10))

            elements.append(Paragraph(f"<b>Sources:</b> {item.sources}", styles["Normal"]))
            elements.append(Spacer(1, 20))

        doc.build(elements)

        # Retrieve the data from the buffer and encode it in base64
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # In Reflex, you can download binary data directly
        return rx.download(data=pdf_data, filename="chat_history.pdf")
