import reflex as rx

from DOCU_AI.components.navbar import navbar
from DOCU_AI.states.rag_state import ChatState

def chat() -> rx.Component:
    return rx.vstack(
        navbar(),

        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.hstack(
                        rx.icon(tag="message-square", size=24, color="#2563eb"),
                        rx.heading("Secure AI Assistant", size="6", color="#0f172a"),
                        spacing="2",
                        align="center",
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon(tag="plus", size=18),
                        "New Chat",
                        on_click=ChatState.clear_history,
                        variant="soft",
                        color_scheme="blue",
                        size="2",
                        radius="full",
                        _hover={"transform": "scale(1.05)"},
                        transition="all 0.2s"
                    ),
                    align="center",
                    padding_y="20px",
                    border_bottom="1px solid #e2e8f0",
                    width="100%",
                ),

                # Chat Messages Area
                rx.box(
                    rx.vstack(
                        rx.cond(
                            ChatState.history.length() == 0,
                            rx.vstack(
                                rx.icon(tag="bot", size=48, color="#cbd5e1", margin_bottom="10px"),
                                rx.text("I am ready to answer questions based on your uploaded documents.", color="#64748b", text_align="center"),
                                align="center",
                                justify="center",
                                height="100%",
                            )
                        ),
                        rx.foreach(
                            ChatState.history,
                            lambda item: message_pair(item)
                        ),
                        
                        rx.cond(
                            ChatState.is_loading,
                            rx.hstack(
                                rx.spinner(size="2", color="#2563eb"),
                                rx.text("Thinking...", color="#64748b", font_size="14px", font_weight="500"),
                                padding="16px",
                                background="white",
                                border_radius="16px 16px 16px 0",
                                box_shadow="0 4px 15px rgba(0,0,0,0.05)",
                                align="center",
                                spacing="3",
                                margin_top="10px"
                            )
                        ),
                        width="100%",
                        spacing="4"
                    ),
                    width="100%",
                    flex="1",
                    overflow_y="auto",
                    padding_y="20px",
                    padding_x="10px",
                    style={"&::-webkit-scrollbar": {"width": "6px"}, "&::-webkit-scrollbar-thumb": {"background": "#cbd5e1", "border_radius": "3px"}}
                ),

                # Input Area
                rx.form(
                    rx.box(
                        rx.hstack(
                            rx.input(
                                name="chat_input",
                                placeholder="Ask anything about your documents...",
                                width="100%",
                                size="3",
                                radius="full",
                                height="50px",
                                border="1px solid #cbd5e1",
                                background_color="#ffffff",
                                color="#1e293b"
                            ),
                            rx.button(
                                rx.icon(tag="send", size=18),
                                type="submit",
                                size="3",
                                radius="full",
                                background="#2563eb",
                                color="white",
                                padding="16px",
                                box_shadow="0 4px 14px rgba(37,99,235,0.3)",
                                _hover={"background": "#1d4ed8", "transform": "scale(1.05)"},
                                transition="all 0.2s"
                            ),
                            width="100%",
                            spacing="3",
                            align="center"
                        ),
                        width="100%",
                        padding_top="20px",
                        border_top="1px solid #e2e8f0",
                    ),
                    on_submit=ChatState.handle_submit,
                    reset_on_submit=True,
                    width="100%"
                ),

                width="100%",
                max_width="900px",
                margin="0 auto",
                background="white",
                border_radius="24px",
                box_shadow="0 20px 40px -15px rgba(0,0,0,0.1)",
                padding="30px",
                height="85vh",
                overflow="hidden"
            ),
            width="100%",
            background="#f1f5f9",
            padding="40px 20px",
            min_height="100vh"
        )
    )

def message_pair(item):
    return rx.vstack(
        # User Message
        rx.hstack(
            rx.spacer(),
            rx.box(
                rx.text(item.question, color="white", font_size="15px"),
                background="#2563eb",
                padding="14px 20px",
                border_radius="20px 20px 0px 20px",
                box_shadow="0 4px 15px rgba(37,99,235,0.2)",
                max_width="75%"
            ),
            width="100%"
        ),
        
        # AI Message
        rx.hstack(
            rx.box(
                rx.icon(tag="bot", size=24, color="#10b981"),
                padding="10px",
                background="#ecfdf5",
                border_radius="full",
                margin_right="10px"
            ),
            rx.vstack(
                rx.box(
                    rx.text(item.answer, white_space="pre-wrap", color="#334155", font_size="15px", line_height="1.6"),
                    background="white",
                    padding="16px 20px",
                    border_radius="0px 20px 20px 20px",
                    box_shadow="0 4px 15px rgba(0,0,0,0.05)",
                    border="1px solid #f1f5f9"
                ),
                rx.cond(
                    item.sources != "",
                    rx.hstack(
                        rx.icon(tag="info", size=12, color="#94a3b8"),
                        rx.text(f"Source: {item.sources}", font_size="12px", color="#94a3b8"),
                        align="center",
                        spacing="1",
                        margin_top="4px",
                        padding_left="10px"
                    )
                ),
                align="start",
                max_width="85%"
            ),
            width="100%",
            margin_top="15px"
        ),
        width="100%",
        spacing="4"
    )