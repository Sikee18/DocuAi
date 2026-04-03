import reflex as rx

def hero():
    return rx.vstack(
        rx.center(
            rx.vstack(
                rx.text("Enterprise Ready", font_size="14px", font_weight="700", color="#2563eb", text_transform="uppercase", margin_bottom="4px"),
                rx.heading(
                    "AI Document Intelligence Search & Retrieval",
                    size="9",
                    weight="bold",
                    text_align="center",
                ),
                rx.text(
                    "Instantly chat with your internal documents using advanced open-source RAG models. Secure, private, and incredibly fast.",
                    color="#64748b",
                    font_size="20px",
                    text_align="center",
                    max_width="600px",
                    margin_y="24px",
                ),
                rx.hstack(
                    rx.button(
                        "Get Started Now",
                        rx.icon(tag="arrow-right"),
                        on_click=rx.redirect("/upload"),
                        background="#2563eb",
                        color="white",
                        size="3",
                    ),
                    rx.button(
                        "View History",
                        on_click=rx.redirect("/history"),
                        variant="outline",
                        size="3",
                        color_scheme="gray",
                    ),
                    spacing="5",
                    justify="center"
                ),
                align_items="center",
                width="100%",
                padding_y="100px",
            ),
            width="100%",
        ),
        # Statistics/Feature Cards Row
        rx.hstack(
            feature_card("Fast Retrieval", "Sub-second semantic search", "zap"),
            feature_card("Secure Memory", "Session-based local vector store", "lock"),
            feature_card("Open Models", "Powered by Llama 3 on Groq", "cpu"),
            spacing="8",
            margin_top="60px",
            justify="center",
            width="100%",
            wrap="wrap"
        ),
        width="100%",
        padding="20px",
        min_height="80vh",
        background="radial-gradient(circle at top, #f8fafc 0%, #ffffff 100%)",
        align_items="center",
        justify_content="center"
    )

def feature_card(title: str, description: str, icon_tag: str):
    return rx.vstack(
        rx.box(
            rx.icon(tag=icon_tag, color="#2563eb"),
            padding="12px",
            background="#eff6ff",
            border_radius="12px",
            margin_bottom="12px"
        ),
        rx.text(title, font_weight="700", font_size="18px", color="#0f172a"),
        rx.text(description, color="#64748b", font_size="14px", text_align="center"),
        align="center",
        padding="24px",
        background="white",
        border_radius="16px",
        border="1px solid #e2e8f0",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05)",
        width="280px",
    )
