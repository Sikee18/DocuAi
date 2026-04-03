# """Welcome to Reflex! This file outlines the steps to create a basic app."""

# import reflex as rx

# from rxconfig import config


# class State(rx.State):
#     """The app state."""


# def index() -> rx.Component:
#     # Welcome Page (Index)
#     return rx.container(
#         rx.color_mode.button(position="top-right"),
#         rx.vstack(
#             rx.heading("Welcome to Reflex!", ),
#             rx.text(
#                 "Get started by editing ",
#                 rx.code(f"{config.app_name}/{config.app_name}.py"),
#                 ,
#             ),
#             rx.link(
#                 rx.button("Check out our docs!"),
#                 href="https://reflex.dev/docs/getting-started/introduction/",
#                 is_external=True,
#             ),
#             spacing="5",
#             justify="center",
#             min_height="85vh",
#         ),
#     )


# app = rx.App()
# app.add_page(index)

# import reflex as rx
# from RAG_PROJECT.components.navbar import navbar
# from RAG_PROJECT.components.footer import footer
# from RAG_PROJECT.components.hero import hero
# def home():
#     return rx.box(
#         navbar(),
#         hero(),
#         footer(),
#         bg="white",
#         min_height="100vh",
#     )


# def upload_documents():
#     return rx.text("Upload your documnets here!")

# def History():
#     return rx.text("History of Perivous chats")

# def about():
#     return rx.text("about the app.....")

# app=rx.App()
# app.add_page(home,route ='/')
# app.add_page(upload_documents, route='/upload_documents')
# app.add_page(History, route= '/history')
# app.add_page(about,route='/about')

import reflex as rx

from DOCU_AI.pages.about import about
from DOCU_AI.pages.home import home
from DOCU_AI.pages.upload import upload
from DOCU_AI.pages.chat import chat
from DOCU_AI.pages.history import history
from DOCU_AI.pages.insights import insights

app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
    )
)

app.add_page(home, route="/")
app.add_page(upload, route="/upload")
app.add_page(chat, route="/chat")
app.add_page(history, route="/history")
app.add_page(about, route="/about")
app.add_page(insights, route="/insights")



