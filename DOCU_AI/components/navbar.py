import reflex as rx

def navbar():
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon(tag="layers", size=28, color="#2563eb"),
                rx.text("DocuSearch AI", font_size="22px", font_weight="800", color="#0f172a", letter_spacing="-0.5px"),
                align="center",
                spacing="2"
            ),
            rx.spacer(),
            rx.hstack(
                rx.link("Home", href="/", style={"_hover": {"color": "#2563eb", "transform": "scale(1.05)"}, "transition": "all 0.2s"}, font_weight="600", color="#475569"),
                rx.link("Upload", href="/upload", style={"_hover": {"color": "#2563eb", "transform": "scale(1.05)"}, "transition": "all 0.2s"}, font_weight="600", color="#475569"),
                rx.link("Chat", href="/chat", style={"_hover": {"color": "#2563eb", "transform": "scale(1.05)"}, "transition": "all 0.2s"}, font_weight="600", color="#475569"),
                rx.link("History", href="/history", style={"_hover": {"color": "#2563eb", "transform": "scale(1.05)"}, "transition": "all 0.2s"}, font_weight="600", color="#475569"),
                spacing="6",
            ),
            width="100%",
            padding_x="30px",
            padding_y="15px",
            max_width="1200px",
            margin="0 auto"
        ),
        width="100%",
        position="sticky",
        top="0",
        z_index="50",
        background="rgba(255, 255, 255, 0.85)",
        backdrop_filter="blur(12px)",
        border_bottom="1px solid rgba(226, 232, 240, 0.8)",
        box_shadow="0 4px 20px -2px rgba(0, 0, 0, 0.05)"
    )
