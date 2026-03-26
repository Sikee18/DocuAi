import reflex as rx
from DOCU_AI.components.navbar import navbar
from DOCU_AI.states.rag_state import ChatState

def history():
    return rx.vstack(
        navbar(),

        rx.vstack(
            rx.hstack(
                rx.icon(tag="history", size=28, color="#0f172a"),
                rx.heading("Conversation History", size="7", color="#0f172a", font_weight="800"),
                align="center",
                spacing="3",
                margin_bottom="20px"
            ),

            rx.cond(
                ChatState.history.length() == 0,
                rx.box(
                    rx.vstack(
                        rx.icon(tag="clock", size=48, color="#cbd5e1", margin_bottom="10px"),
                        rx.text("No chat history available.", font_weight="600", color="#475569", size="4"),
                        rx.text("Your past interactions will appear here.", color="#94a3b8"),
                        align="center",
                        padding="60px",
                        border="2px dashed #e2e8f0",
                        border_radius="16px",
                        background="#f8fafc",
                        width="100%"
                    ),
                    width="100%"
                ),
                rx.vstack(
                    rx.foreach(
                        ChatState.history,
                        lambda item: history_card(item)
                    ),
                    
                    rx.hstack(
                        rx.button(
                            rx.icon(tag="trash-2", size=16),
                            "Clear History",
                            color_scheme="red",
                            variant="soft",
                            size="3",
                            on_click=ChatState.clear_history,
                            style={"_hover": {"background": "#fee2e2"}}
                        ),
                        rx.button(
                            rx.icon(tag="download", size=16),
                            "Download PDF",
                            color_scheme="blue",
                            size="3",
                            on_click=ChatState.download_chat,
                            box_shadow="0 4px 14px 0 rgba(0, 118, 255, 0.39)",
                        ),
                        spacing="4",
                        margin_top="30px",
                        justify="end",
                        width="100%"
                    ),
                    width="100%",
                    spacing="4"
                )
            ),
            width="100%",
            max_width="800px",
            margin="0 auto",
            padding="40px",
            background="white",
            border_radius="24px",
            box_shadow="0 10px 40px -10px rgba(0,0,0,0.05)",
            border="1px solid #e2e8f0",
            margin_top="40px"
        ),

        width="100%",
        min_height="100vh",
        background="#f8fafc",
        padding_bottom="60px"
    )

def history_card(item):
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(tag="user", size=16, color="#2563eb"),
                rx.text(item.question, font_weight="700", color="#1e293b", size="3"),
                align="center",
                spacing="2",
                margin_bottom="10px"
            ),
            rx.box(
                rx.text(item.answer, color="#475569", line_height="1.6", font_size="15px"),
                padding="16px",
                background="#f1f5f9",
                border_radius="12px",
                border_left="4px solid #10b981",
                width="100%",
                margin_bottom="10px"
            ),
            rx.cond(
                item.sources != "",
                rx.hstack(
                    rx.badge(item.sources, color_scheme="gray", variant="soft", radius="full"),
                    align="center",
                    margin_top="5px"
                )
            ),
            align="start",
            width="100%"
        ),
        padding="24px",
        background="white",
        border="1px solid #e2e8f0",
        border_radius="16px",
        box_shadow="0 2px 10px rgba(0,0,0,0.02)",
        width="100%",
        style={"_hover": {"box_shadow": "0 10px 15px -3px rgba(0,0,0,0.05)", "transform": "translateY(-1px)"}, "transition": "all 0.2s ease"}
    )
