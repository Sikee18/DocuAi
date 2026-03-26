import reflex as rx

def hero():
    return rx.vstack(
        rx.box(
            rx.text("Enterprise Ready", font_size="14px", font_weight="700", color="#2563eb", text_transform="uppercase", margin_bottom="4px", text_align="center"),
            rx.heading(
                rx.text.span("AI Document Intelligence", background_image="linear-gradient(90deg, #1e3a8a, #2563eb, #0ea5e9)", background_clip="text", color="transparent"),
                rx.text.span("\nSearch & Retrieval", color="#0f172a"),
                size="9",
                weight="bold",
                text_align="center",
                line_height="1.2",
                style={"font_size": "clamp(3rem, 5vw, 4rem)", "letter_spacing": "-1px"}
            ),
            rx.text(
                "Instantly chat with your internal documents using advanced open-source RAG models. Secure, private, and incredibly fast.",
                color="#64748b",
                font_size="20px",
                text_align="center",
                max_width="600px",
                margin_y="24px",
                margin_x="auto"
            ),
            rx.hstack(
                rx.button(
                    "Get Started Now",
                    rx.icon(tag="arrow-right", size=18),
                    on_click=rx.redirect("/upload"),
                    background="linear-gradient(90deg, #2563eb, #3b82f6)",
                    color="white",
                    size="4",
                    radius="full",
                    padding_x="32px",
                    padding_y="24px",
                    font_size="18px",
                    font_weight="600",
                    box_shadow="0 10px 25px -5px rgba(37, 99, 235, 0.4)",
                    style={"_hover": {"transform": "translateY(-2px)", "box_shadow": "0 20px 25px -5px rgba(37, 99, 235, 0.5)"}, "transition": "all 0.3s ease"}
                ),
                rx.button(
                    "View History",
                    on_click=rx.redirect("/history"),
                    variant="outline",
                    size="4",
                    radius="full",
                    color_scheme="gray",
                    padding_x="32px",
                    padding_y="24px",
                    font_size="18px",
                    font_weight="600",
                    style={"_hover": {"background": "#f1f5f9"}, "transition": "all 0.3s ease"}
                ),
                spacing="5",
                justify="center"
            ),
            width="100%",
            margin_top="10%"
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
        align="center"
    )

def feature_card(title: str, description: str, icon_tag: str):
    return rx.vstack(
        rx.box(
            rx.icon(tag=icon_tag, size=24, color="#2563eb"),
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
        style={"_hover": {"transform": "translateY(-5px)", "box_shadow": "0 20px 25px -5px rgba(0, 0, 0, 0.1)"}, "transition": "all 0.3s ease"}
    )