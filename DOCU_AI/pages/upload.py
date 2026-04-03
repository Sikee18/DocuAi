import reflex as rx
import os
from langdetect import detect
import pypdf

from DOCU_AI.components.navbar import navbar
from DOCU_AI.components.footer import footer
from DOCU_AI.backend.rag import build_vectorstore

# Hardcode relative to execution dir so it doesn't break when Reflex moves upload.py to .web
UPLOAD_DIR = os.path.join(os.getcwd(), "documents")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class UploadedFile(rx.Base):
    filename: str
    language: str

class UploadState(rx.State):
    files: list[UploadedFile] = []
    is_uploading: bool = False
    processing_step: str = "Initializing..."
    show_success_dialog: bool = False

    def close_dialog(self):
        self.show_success_dialog = False

    def load_files(self):
        new_files = []
        if os.path.exists(UPLOAD_DIR):
            for f in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, f)
                lang = "unknown"
                try:
                    if f.endswith('.txt') or f.endswith('.csv'):
                        with open(file_path, 'r', encoding='utf-8') as text_file:
                            content = text_file.read(500)
                            lang = detect(content)
                    elif f.endswith('.pdf'):
                        import fitz
                        with fitz.open(file_path) as doc:
                            if len(doc) > 0:
                                content = doc[0].get_text()[:500]
                                if "CamScanner" in content or len(content.strip()) < 100:
                                    lang = "Scanned (Gemini OCR)"
                                else:
                                    lang = detect(content)
                    elif f.endswith('.docx'):
                        import docx2txt
                        content = docx2txt.process(file_path)[:500]
                        lang = detect(content)
                    elif f.lower().endswith(('.png', '.jpg', '.jpeg')):
                        lang = "Image (Gemini OCR)"
                except Exception:
                    lang = "unknown"
                new_files.append(UploadedFile(filename=f, language=lang))
        self.files = new_files

    def delete_file(self, filename: str):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            self.load_files()
            build_vectorstore()

    def clear_knowledge_base(self):
        """Removes all files from the knowledge base."""
        if os.path.exists(UPLOAD_DIR):
            for f in os.listdir(UPLOAD_DIR):
                try: os.remove(os.path.join(UPLOAD_DIR, f))
                except: pass
        self.load_files()
        build_vectorstore()

    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        self.is_uploading = True
        self.processing_step = "Reading files..."
        yield
        for file in files:
            save_path = os.path.join(UPLOAD_DIR, file.filename)
            self.processing_step = f"Saving {file.filename}..."
            yield
            content = await file.read()
            with open(save_path, "wb") as f:
                f.write(content)
        self.processing_step = "Vectorizing Knowledge (Indexing)..."
        yield
        build_vectorstore()
        self.load_files()
        self.is_uploading = False
        self.show_success_dialog = True
        yield rx.clear_selected_files("upload1")

def upload():
    return rx.vstack(
        navbar(),
        rx.vstack(
            rx.vstack(
                rx.heading("Data Knowledge Base", size="7", color="#0f172a"),
                rx.text("Upload PDF or text files to train your local AI.", color="#64748b"),
                align_items="center",
                padding_y="40px",
                width="100%",
            ),
            rx.box(
                rx.upload(
                    rx.vstack(
                        rx.icon(tag="upload", color="#3b82f6"),
                        rx.text("Drag and drop your files here", font_weight="600"),
                        align="center", justify="center", padding="40px",
                    ),
                    id="upload1", border="2px dashed #cbd5e1", 
                    background="#f8fafc", width="100%",
                ),
                rx.cond(
                    rx.selected_files("upload1"),
                    rx.vstack(
                        rx.text("Queue", font_weight="600"),
                        rx.foreach(
                            rx.selected_files("upload1"),
                            lambda f: rx.hstack(
                                rx.icon(tag="file", color="#3b82f6"),
                                rx.text(f, color="#1e293b", font_weight="500"),
                                background="#f1f5f9", padding="8px 16px", border_radius="8px", width="100%"
                            )
                        ),
                        width="100%",
                        margin_top="10px",
                    )
                ),
                rx.button(
                    "Sync & Upload Knowledge Base",
                    on_click=UploadState.handle_upload(rx.upload_files("upload1")),
                    width="100%", color_scheme="blue", margin_top="24px",
                    disabled=rx.selected_files("upload1").length() == 0,
                ),
                width="100%", max_width="600px", background="white", padding="40px", border_radius="24px",
                box_shadow="0 10px 40px -10px rgba(0,0,0,0.08)", border="1px solid #e2e8f0"
            ),
            rx.box(
                rx.hstack(
                    rx.heading("Active Knowledge Base", size="5", color="#0f172a"),
                    rx.spacer(),
                    rx.button(
                        "Clear All", on_click=UploadState.clear_knowledge_base,
                        color_scheme="red", disabled=UploadState.files.length() == 0,
                    ),
                    width="100%", margin_bottom="20px", align="center",
                ),
                rx.cond(
                    UploadState.files.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            UploadState.files,
                            lambda file: rx.hstack(
                                rx.hstack(
                                    rx.icon(tag="check", color="#10b981"),
                                    rx.text(file.filename, font_weight="500", color="#334155"),
                                    rx.badge("Detected: " + file.language, color_scheme="blue"),
                                    spacing="3", align="center"
                                ),
                                rx.spacer(),
                                rx.button(
                                    rx.icon(tag="trash"),
                                    on_click=UploadState.delete_file(file.filename),
                                    color_scheme="red"
                                ),
                                width="100%", padding="16px", background="white", border_radius="12px",
                                border="1px solid #e2e8f0"
                            )
                        ),
                        width="100%", spacing="3"
                    ),
                    rx.box(
                        rx.text("No documents uploaded yet.", color="#94a3b8", text_align="center"),
                        width="100%"
                    )
                ),
                width="100%", max_width="600px", margin_top="40px"
            ),
            rx.cond(
                UploadState.show_success_dialog,
                rx.box(
                    rx.vstack(
                        rx.icon(tag="check", color="#10b981"),
                        rx.heading("Upload Complete", size="5"),
                        rx.hstack(
                            rx.button("Stay", on_click=UploadState.close_dialog),
                            rx.button("Chat", on_click=rx.redirect("/chat"), color_scheme="blue"),
                            spacing="4", margin_top="20px"
                        ),
                        align="center", background="white", padding="40px", border_radius="24px",
                    ),
                    position="fixed", top="0", left="0", width="100vw", height="100vh", background="rgba(15, 23, 42, 0.4)",
                    backdrop_filter="blur(4px)", z_index="100", display="flex", align_items="center", justify_content="center"
                )
            ),
            align_items="center",
            width="100%",
            background="#f8fafc",
            min_height="90vh",
            padding_bottom="60px",
        ),
        spacing="0", on_mount=UploadState.load_files, width="100%"
    )
