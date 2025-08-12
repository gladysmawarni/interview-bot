import reflex as rx

config = rx.Config(
    app_name="interview_bot",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
)