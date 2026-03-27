import reflex as rx

config = rx.Config(
    app_name="DOCU_AI",
    cors_allowed_origins=[
        "http://localhost:3000",
        "https://sikee18-docuai.hf.space"
    ],
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)