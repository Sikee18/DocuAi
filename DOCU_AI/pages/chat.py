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
                        rx.icon(tag="message_square", color="#2563eb"),
                        rx.heading("Secure AI Assistant", color="#0f172a"),
                        spacing="2",
                        align="center",
                    ),
                    rx.spacer(),
                    rx.select(
                        ["English", "Tamil", "Hindi", "Telugu", "Kannada", "Malayalam", "Bengali"],
                        value=ChatState.preferred_language,
                        on_change=ChatState.set_preferred_language,
                        color_scheme="blue",
                    ),
                    rx.button(
                        rx.icon(tag="plus"),
                        "New Chat",
                        on_click=ChatState.clear_history,
                        color_scheme="blue",
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
                                rx.icon(tag="bot", color="#cbd5e1", margin_bottom="10px"),
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
                                rx.spinner(color="#2563eb"),
                                rx.text("Thinking...", color="#64748b", font_size="14px", font_weight="500"),
                                padding="16px",
                                background="white",
                                border_radius="16px",
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
                                height="50px",
                                border="1px solid #cbd5e1",
                                background_color="#ffffff",
                                color="#1e293b"
                            ),
                            rx.button(
                                rx.icon(tag="send"),
                                type="submit",
                                background="#2563eb",
                                color="white",
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
            rx.vstack(
                rx.box(
                    rx.text(item.question, color="white", font_size="15px"),
                    background="#2563eb",
                    padding="14px 20px",
                    border_radius="20px",
                    box_shadow="0 4px 15px rgba(37,99,235,0.2)",
                ),
                rx.text(item.question_language, font_size="10px", color="#94a3b8", text_align="right", width="100%"),
                max_width="75%",
                align_items="flex-end"
            ),
            width="100%"
        ),
        
        # AI Message
        rx.hstack(
            rx.box(
                rx.icon(tag="bot", color="#10b981"),
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
                    border_radius="20px",
                    box_shadow="0 4px 15px rgba(0,0,0,0.05)",
                    border="1px solid #f1f5f9"
                ),
                rx.hstack(
                    rx.badge(item.response_language, color_scheme="blue"),
                    rx.cond(
                        item.sources != "",
                        rx.hstack(
                            rx.icon(tag="info", color="#94a3b8"),
                            rx.text(f"Source: {item.sources}", font_size="12px", color="#94a3b8"),
                            align="center",
                            spacing="1",
                        )
                    ),
                    rx.cond(
                        item.sources == "System Intelligence",
                        rx.button(
                            "View Insights Dashboard",
                            rx.icon(tag="layout_dashboard"),
                            on_click=rx.redirect("/insights"),
                            color_scheme="blue",
                        )
                    ),
                    spacing="3",
                    align="center",
                    margin_top="4px",
                    padding_left="10px"
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
