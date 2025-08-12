### Main app file
import reflex as rx
from .components.chatbot import chat, action_bar, info_form # custom functions

class State(rx.State):
    """The app state."""

# homepage (form)
def index() -> rx.Component:
    # Welcome Page (Index)
    return rx.center(
        rx.vstack(
            rx.color_mode.button(position="absolute", top="1rem", right="1rem"), # dark/light mode button
            info_form(),
            spacing="9",
        ),
        min_height="100vh",
    )

# chat page 
def chatbot() -> rx.Component:
    return rx.center(
        rx.vstack(
            chat(),
            action_bar(),
            align="center",
        )
    )


# define app
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="purple",
    ),
)
app.add_page(index)
app.add_page(chatbot, route="/chat")
