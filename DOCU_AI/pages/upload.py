import reflex as rx
import os

from DOCU_AI.components.navbar import navbar
from DOCU_AI.components.footer import footer
from DOCU_AI.backend.rag import build_vectorstore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "documents")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class UploadState(rx.State):
    files: list[str] = []
    is_uploading: bool = False
    show_success_dialog: bool = False

    def close_dialog(self):
        self.show_success_dialog = False

    def load_files(self):
        if os.path.exists(UPLOAD_DIR):
            self.files = os.listdir(UPLOAD_DIR)

    def delete_file(self, filename: str):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            self.load_files()
            build_vectorstore()

    async def handle_upload(self, files: list[rx.UploadFile]):
        self.is_uploading = True
        yield
        
        for file in files:
            save_path = os.path.join(UPLOAD_DIR, file.filename)
            content = await file.read()
            with open(save_path, "wb") as f:
                f.write(content)
        
        self.load_files()
        build_vectorstore()
        
        self.is_uploading = False
        self.show_success_dialog = True
        yield rx.clear_selected_files("upload1")

def upload():
    return rx.vstack(
        navbar(),

        rx.vstack(
            rx.heading("Data Knowledge Base", size="8", color="#0f172a", font_weight="800", margin_bottom="10px"),
            rx.text("Upload PDF or text files to securely train your local RAG agent.", color="#64748b", font_size="16px", margin_bottom="30px"),
            
            # UPload Card
            rx.box(
                rx.upload(
                    rx.vstack(
                        rx.icon(tag="upload-cloud", size=48, color="#3b82f6", margin_bottom="15px"),
                        rx.text("Drag and drop your files here", font_weight="600", font_size="18px", color="#1e293b"),
                        rx.text("or click to browse", color="#64748b", font_size="14px"),
                        align="center",
                        justify="center",
                        padding="40px",
                    ),
                    id="upload1",
                    border="2px dashed #cbd5e1",
                    border_radius="16px",
                    background="#f8fafc",
                    width="100%",
                    style={"_hover": {"border_color": "#3b82f6", "background": "#eff6ff"}, "transition": "all 0.2s"},
                ),

                rx.cond(
                    rx.selected_files("upload1"),
                    rx.vstack(
                        rx.text("Queued for upload:", font_weight="600", font_size="14px", color="#475569", margin_top="20px"),
                        rx.foreach(
                            rx.selected_files("upload1"),
                            lambda f: rx.hstack(
                                rx.icon(tag="file-text", size=16, color="#3b82f6"),
                                rx.text(f, color="#1e293b", font_weight="500"),
                                background="#f1f5f9",
                                padding="8px 16px",
                                border_radius="8px",
                                width="100%"
                            )
                        ),
                        width="100%"
                    ),
                    rx.box()
                ),

                rx.cond(
                    UploadState.is_uploading,
                    rx.hstack(
                        rx.spinner(size="3"),
                        rx.text("Processing documents...", color="#3b82f6", font_weight="500"),
                        align="center",
                        justify="center",
                        spacing="3",
                        margin_top="24px",
                        width="100%",
                        padding="12px",
                        background="#eff6ff",
                        border_radius="8px"
                    ),
                    rx.button(
                        "Upload Documents",
                        rx.icon(tag="upload", size=16),
                        on_click=UploadState.handle_upload(rx.upload_files(upload_id="upload1")),
                        width="100%",
                        size="4",
                        color_scheme="blue",
                        margin_top="24px",
                        border_radius="8px",
                        box_shadow="0 4px 14px 0 rgba(0, 118, 255, 0.39)",
                        style={"_hover": {"transform": "translateY(-1px)", "box_shadow": "0 6px 20px rgba(0,118,255,0.23)"}}
                    )
                ),

                width="100%",
                max_width="600px",
                background="white",
                padding="40px",
                border_radius="24px",
                box_shadow="0 10px 40px -10px rgba(0,0,0,0.08)",
                border="1px solid #e2e8f0"
            ),

            # Uploaded Files Section
            rx.box(
                rx.heading("Active Knowledge Base", size="5", color="#0f172a", margin_bottom="20px"),
                rx.cond(
                    UploadState.files.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            UploadState.files,
                            lambda file: rx.hstack(
                                rx.hstack(
                                    rx.icon(tag="check-circle", color="#10b981", size=18),
                                    rx.text(file, font_weight="500", color="#334155"),
                                    spacing="3",
                                    align="center"
                                ),
                                rx.spacer(),
                                rx.button(
                                    rx.icon(tag="trash-2", size=16),
                                    on_click=UploadState.delete_file(file),
                                    color_scheme="red",
                                    variant="soft",
                                    size="2",
                                    border_radius="8px"
                                ),
                                width="100%",
                                padding="16px",
                                background="white",
                                border_radius="12px",
                                border="1px solid #e2e8f0",
                                box_shadow="0 2px 4px rgba(0,0,0,0.02)"
                            )
                        ),
                        width="100%",
                        spacing="3"
                    ),
                    rx.box(
                        rx.text("No documents uploaded yet. Add files above to train the AI.", color="#94a3b8", text_align="center", padding="30px", border="1px dashed #cbd5e1", border_radius="12px"),
                        width="100%"
                    )
                ),
                width="100%",
                max_width="600px",
                margin_top="40px"
            ),

            # SUCCESS MODAL POPUP
            rx.cond(
                UploadState.show_success_dialog,
                rx.box(
                    rx.vstack(
                        rx.icon(tag="check-circle", color="#10b981", size=48, margin_bottom="10px"),
                        rx.heading("Upload Complete", size="6", color="#0f172a"),
                        rx.text("Your documents have been securely processed and added to the Knowledge Base.", text_align="center", color="#475569"),
                        rx.text("Would you like to ask the AI questions about these documents now?", text_align="center", font_weight="500", margin_top="10px", color="#1e293b"),
                        
                        rx.hstack(
                            rx.button("Stay Here", variant="outline", color_scheme="gray", size="3", on_click=UploadState.close_dialog),
                            rx.button("Chat with AI", rx.icon(tag="message-square", size=16), color_scheme="blue", size="3", on_click=rx.redirect("/chat")),
                            spacing="4",
                            margin_top="20px"
                        ),
                        
                        align="center",
                        background="white",
                        padding="40px",
                        border_radius="24px",
                        box_shadow="0 25px 50px -12px rgba(0, 0, 0, 0.25)",
                        max_width="450px"
                    ),
                    position="fixed",
                    top="0",
                    left="0",
                    width="100vw",
                    height="100vh",
                    background="rgba(15, 23, 42, 0.4)",
                    backdrop_filter="blur(4px)",
                    z_index="100",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    padding="20px"
                )
            ),

            width="100%",
            align="center",
            padding_top="60px",
            padding_bottom="100px",
            background="#f8fafc",
            min_height="90vh"
        ),
        spacing="0",
        on_mount=UploadState.load_files,
        width="100%"
    )