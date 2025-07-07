import os
import chainlit as cl
from dotenv import load_dotenv
from agents import Agent, AsyncOpenAI, Runner, RunConfig, OpenAIChatCompletionsModel, function_tool

# Load .env variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
gemini_base_url = os.getenv("GEMINI_BASE_URL")

# Gemini Client setup
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url=gemini_base_url,
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

run_config = RunConfig(
    model=model,
    tracing_disabled=True,
)

# Tools
@function_tool
def goat_listing_info():
    """Goat listing upload help"""
    return "Admin can upload goats from the Admin Panel by entering Name, Age, Price, and uploading a video."

@function_tool
def contact_help():
    """How to contact the farm"""
    return "Aap 'Contact' page pr ja kar form bhar kar rabta kar skty hain ya WhatsApp button se bhi baat kar skty hain."

@function_tool
def buy_goat_guide():
    """How to buy a goat"""
    return "Bakri pasand aane par WhatsApp button dabayein ya contact form se rabta karen. Admin aap se rabta karega."

# 🧠 Akhtar Goat Farm Assistant
agent = Agent(
    name="Akhtar Farm Assistant 🐐",
    instructions="""
You are the helpful assistant for Akhtar Goat Farm – a livestock selling platform based in North Karachi.

Only answer what the user asks and answer in roman urdu with emojee, avoid giving extra details.

Farm Info:
- Goats are listed on the 'Goats' page with age, price, and video.
- Clicking on a goat shows detailed view + WhatsApp button.
- Admin uploads goats via Admin Panel.
- Admin Whatsapp number: +92 315 2491432
- Contact available via form or WhatsApp.
- Farm is real and based in Karachi.

If user asks:
- "Kahan ka farm hai?": reply "Ye North Karachi mein hai."
- "Payment kaise karni hai?": reply "Admin WhatsApp pe aapko detail dega."
- "Delivery hai?": reply "Karachi mein delivery ho sakti hai, WhatsApp pr confirm karein."

""",
    tools=[goat_listing_info, contact_help, buy_goat_guide]
)


# Start of chat
@cl.on_chat_start
async def start():
    cl.user_session.set("history", [])
    await cl.Message(content="👋 Akhtar Goat Farm mein khushamdeed! Kisi bhi madad ke liye poochhiye.").send()


@cl.on_message
async def main(message: cl.Message):
    history = cl.user_session.get("history") or []
    history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")
    await msg.send()

    result = Runner.run_streamed(
        agent,
        input=history,
        run_config=run_config,
    )

    async for event in result.stream_events():
        delta = getattr(getattr(event, "data", None), "delta", None)
        if delta:
            msg.content += delta
            await msg.update()

    history.append({"role": "assistant", "content": msg.content})
    cl.user_session.set("history", history)