import reflex as rx

config = rx.Config(
    app_name="DOCU_AI",
    cors_allowed_origins=[
        "https://sikee18-docuai.hf.space",
        "https://sikee18-docuai-final.hf.space",
        "https://sikee18-docuai-official.hf.space",
    ],
    api_url="https://sikee18-docuai-official.hf.space",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)