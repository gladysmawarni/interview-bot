# library
from openai import AsyncOpenAI
from . import style

import reflex as rx

# API KEY
OPENAI_API_KEY = ""

# App state
class State(rx.State):
    question: str # user question
    chat_history: list[tuple[str, str]] = [] 
    research_output: str = "" # info about companies + interviewer
    user_background: str = "" # info about user background
    loading: bool = False # show loading icon while research running on background


    # handle form submit
    @rx.event
    async def handle_submit(self, form_data: dict):
        """Handle the form submit."""
        self.loading = True # show loading icon
        yield
        
        client = AsyncOpenAI(
            api_key=OPENAI_API_KEY
        )

        # Call the responses API
        response = await client.responses.create(
            model = "gpt-4.1",
            tools = [{"type": "web_search_preview",
                   }],
            input = f"Research about {form_data['company_name']} in {form_data['location']} and their employee: {form_data['interviewer_name']}"
        )

         # Store research text in state
        self.research_output = response.output_text

        # Store user background in state
        self.user_background = form_data.get("user_background", "")

        # --- done ---
        self.loading = False

        yield rx.redirect('/chat')


    # generate personalized welcome message
    async def generate_welcome(self):
        """Generate a dynamic welcome message from the bot."""
        if self.chat_history:
            return  # don't add if there's already chat history

        client = AsyncOpenAI(api_key=OPENAI_API_KEY)

        system_prompt = f"""
            You are the interviewer for a job interview practice.

            Here is some info about the company and interviewer:
            {self.research_output}

            Here is the user's background:
            {self.user_background}

            Start by greeting the user and asking the first interview question.
            Be friendly and professional.
            """


        session = await client.chat.completions.create(
            model="gpt-5-nano",
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0.7,
        )

        welcome_text = session.choices[0].message.content.strip()

        # append welcome message to chat history to be shown
        self.chat_history.append((None, welcome_text))
        yield


    # openai call function
    async def answer(self):
        client = AsyncOpenAI(
            api_key=OPENAI_API_KEY
        )

        system_prompt = f"""
            You are a recruiter that will conduct a job interview
            Info about the company and the person you will act as:
            {self.research_output}

            User background:
            {self.user_background}
            
            Be friendly and encouraging, and give feedback on user's response.
            Reply in a format of a markdown. No title or headers.
        """

        # Start streaming completion from OpenAI
        session = await client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self.question}
            ],
            temperature=0.7,
            stream=True,
        )

        # Initialize response and update UI
        answer = ""
        self.chat_history.append((self.question, answer))
        self.question = ""
        yield

        # Process streaming response
        async for item in session:
            if hasattr(item.choices[0].delta, "content"):
                if item.choices[0].delta.content is None:
                    break
                answer += item.choices[0].delta.content
                self.chat_history[-1] = (
                    self.chat_history[-1][0],
                    answer,
                )
                yield


# function to show bot and user chat message
def qa(question: str, answer: str) -> rx.Component:
    return rx.box(
        rx.cond(
            question != None,
            rx.box(rx.markdown(question, style=style.question_style), text_align="right"), # user input
            None
        ),
        rx.box(rx.markdown(answer, style=style.answer_style), text_align="left"), # bot output
        margin_y="1em",
    )


# function to show chat box for each message in chat history
def chat() -> rx.Component:
    return rx.box(
        rx.foreach(
            State.chat_history,
            lambda messages: qa(messages[0], messages[1]),
        ),
        on_mount=State.generate_welcome,
        # Add bottom padding to avoid messages under the input bar
        padding_bottom="5rem",  # enough space for input bar height + margin
        overflow_y="auto",
        max_height="calc(100vh - 5rem)",  # make chat scrollable and not overflow screen
        style={
            "scrollbar-width": "none",  # Firefox
            "-ms-overflow-style": "none",  # IE 10+
        },
    )


# chat input box
def action_bar() -> rx.Component:
    return rx.box(
        rx.form(
            rx.hstack(
                rx.input(
                    value=State.question,
                    placeholder="Ask a question",
                    on_change=State.set_question,
                    style=style.input_style,
                    flex="1",
                    name="question",  # important so it’s sent in form_data
                    autoComplete="off"
                ),
                rx.button(
                    "Ask",
                    type="submit",  # form submit button
                    style=style.button_style,
                ),
                spacing="4",
                padding="1rem",
            ),
            on_submit=State.answer,  # Enter or button click both call this
        ),
        position="fixed",
        bottom="1rem",
        backdrop_blur="lg",
        border_top=f"1px solid {rx.color('mauve', 3)}",
        background_color=rx.color("mauve", 2),
        width="50%",
        z_index="1000",
    )

### ---- FORM --- ###
# form field
def form_field(
    label: str, placeholder: str, type: str, name: str
) -> rx.Component:
    return rx.form.field(
        rx.flex(
            rx.form.label(label),
            rx.form.control(
                rx.input(
                    placeholder=placeholder, type=type
                ),
                as_child=True,
            ),
            direction="column",
            spacing="1",
        ),
        name=name,
        width="100%",
    )

# form for interview info
def info_form() -> rx.Component:
    return rx.card(
        rx.flex(
            rx.hstack(
                rx.badge(
                    rx.icon(tag="search", size=32),
                    color_scheme="blue",
                    radius="full",
                    padding="0.65rem",
                ),
                rx.vstack(
                    rx.heading(
                        "Interview Details",
                        size="4",
                        weight="bold",
                    ),
                    rx.text(
                        "Fill the form to conduct research about your upcoming interview",
                        size="2",
                    ),
                    spacing="1",
                    height="100%",
                ),
                height="100%",
                spacing="4",
                align_items="center",
                width="100%",
            ),
            rx.form.root(
                rx.flex(
                    rx.flex(
                        form_field(
                            "Company Name", # label
                            "Company Name", # placeholder
                            "text", # type
                            "company_name", #name
                        ),
                        form_field(
                            "Position Applied",
                            "Position Applied",
                            "text",
                            "position_applied",
                        ),
                        spacing="3",
                        flex_direction=[
                            "column",
                            "row",
                            "row",
                        ],
                    ),
                    rx.flex(
                        form_field(
                            "Interviewer Name",
                            "Interviewer Name",
                            "text",
                            "interviewer_name",
                        ),
                        form_field(
                            "Location", "Location", "tel", "location"
                        ),
                        spacing="3",
                        flex_direction=[
                            "column",
                            "row",
                            "row",
                        ],
                    ),
                    rx.flex(
                        rx.text(
                            "Your Background",
                            style={
                                "font-size": "15px",
                                "font-weight": "500",
                                "line-height": "35px",
                            },
                        ),
                        rx.text_area(
                            placeholder="Briefly describe your experience, skills, and relevant background for this position",
                            name="user_background",
                            resize="vertical",
                        ),
                        direction="column",
                        spacing="1",
                    ),
                    rx.form.submit(
                        rx.button(
                            rx.cond(
                                State.loading,
                                rx.spinner(size="2"),  # show spinner if loading
                                "Research"               # otherwise show text
                            ),
                            disabled=State.loading
                        ),
                        as_child=True,
                    ),
                    direction="column",
                    spacing="2",
                    width="100%",
                ),
                on_submit= State.handle_submit,
                reset_on_submit=False,
            ),
            width="100%",
            direction="column",
            spacing="4",
        ),
        size="3",
    )