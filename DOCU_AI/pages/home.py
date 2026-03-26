import reflex as rx
from DOCU_AI.components.navbar import navbar
from DOCU_AI.components.hero import hero
from DOCU_AI.components.footer import footer

def home():
    return rx.vstack(
        navbar(),
        hero(),
        footer(),
    )

