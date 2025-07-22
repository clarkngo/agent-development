from google.adk.agents import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="tool_agent",
    model="gemini-2.0-flash",
    description="Tool agent",
    instruction=
        """
        You are a helpful agent who can use the following tools:
        - google search
        """,
    tools=[google_search],
)