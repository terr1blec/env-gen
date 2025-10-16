from agents import Agent, Runner, SQLiteSession, OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from agents import set_default_openai_client
import asyncio
from openai_agents.models import OpenAIChatCompletionsModel

async def main():
    custom_client = AsyncOpenAI(base_url="https://api.deepseek.com", api_key="sk-f4605f9bf44d418895fe946cfa17dd7d")
    model = OpenAIChatCompletionsModel(
    model="deepseek-chat",
    openai_client=custom_client
)
    set_default_openai_client(custom_client)
    # Create agent
    agent = Agent(
        name         = "Assistant",
        instructions = "Reply very concisely.",
        model=model
    )

    # Create a session instance
    session = SQLiteSession("conversation_123")

    # First turn
    result = await Runner.run(
        agent,
        "What city is the Golden Gate Bridge in?",
        session = session,
        model = model
    )
    print(result.final_output)  # "San Francisco"

    # Second turn - agent automatically remembers previous context
    result = await Runner.run(
        agent,
        "What state is it in?",
        session = session,
        model   = model
    )
    print(result.final_output)  # "California"

    # Also works with synchronous runner
    result = Runner.run_sync(
        agent,
        "What's the population?",
        session = session,
        model   = model
    )
    print(result.final_output)  # "Approximately 39 million"

if __name__ == "__main__":
    asyncio.run(main())