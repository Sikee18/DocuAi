import reflex as rx

def footer():
    return rx.grid(
        rx.text("© 2026 AI App", text_align="center", color="white"),
        padding="15px",
        bg="linear-gradient(to right, #4facfe, #00f2fe)",
        position="fixed",
        bottom="0",
        width="100%",
    )