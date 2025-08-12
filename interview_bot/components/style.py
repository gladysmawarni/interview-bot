import reflex as rx

# Common style base
shadow = "rgba(0, 0, 0, 0.15) 0px 2px 8px"
chat_margin = "40%"
message_style = dict(
    padding="1em",
    border_radius="5px",
    margin_y="0.5em",
    box_shadow=shadow,
    max_width="50em",
    display="inline-block",
)

# Styles for questions and answers
question_style = message_style | dict(
    margin_left=chat_margin,
    background_color=rx.color("gray", 4),
)
answer_style = message_style | dict(
    margin_right=chat_margin,
    background_color=rx.color("accent", 8),
)

# Styles for input elements
input_style = dict(
    border_width="1px",
    padding="0.5em",
    box_shadow=shadow,
    width="350px",
)
button_style = dict(
    background_color=rx.color("accent", 10),
    box_shadow=shadow,
)

# style for chat container
chat_container_style = {
    "padding_bottom": "5rem",
    "overflow_y": "auto",
    "max_height": "calc(100vh - 5rem)",
    # Hide scrollbar for WebKit browsers (Chrome, Safari)
    "scrollbar_width": "none",  # Firefox
    "-ms-overflow-style": "none",  # IE 10+
}

# Additional CSS to hide scrollbar for WebKit
chat_container_style_webkit = {
    "::-webkit-scrollbar": {
        "display": "none"
    }
}