import reflex as rx

config = rx.Config(
    app_name="DOCU_AI",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)