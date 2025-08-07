import os
import random

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm

# https://docs.litellm.ai/docs/providers/openrouter
# model="openrouter/openai/gpt-4.1",
# model="openrouter/anthropic/claude-3-5-sonnet",

model = LiteLlm(
    model="openrouter/anthropic/claude-3-5-sonnet",
    api_key=os.getenv("OPEN_ROUTER_API_KEY"),
)

def get_dad_joke():
    jokes =[
        "Why don't skeletons fight each other? They don't have the guts.",
        "I used to play piano by ear, but now I use my hands.",
        "Why did the scarecrow win an award? Because he was outstanding in his field.",
    ]
    return random.choice(jokes)

root_agent = Agent(
    name="dad_joke_agent",
    model=model,
    description="Dad joke agent",
    instruction="""
    You are a helpful assistant that can tell dad jokes.
    Only use the tool `get_dad_joke` to tell jokes.
    """,
    tools=[get_dad_joke]
)
