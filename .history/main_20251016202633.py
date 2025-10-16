from agents import Agent, Runner, SQLiteSession
from openai import AsyncOpenAI
from agents import set_default_openai_client
import asyncio

async def main():
    custom_client = AsyncOpenAI(base_url="https://api.openai.com/v1", api_key="sk-proj-1234567890")
    set_default_openai_client(custom_client)
    # Create agent
    agent = Agent(
        name         = "Assistant",
        instructions = "Reply very concisely.",
    )

    # Create a session instance
    session = SQLiteSession("conversation_123")

    # First turn
    result = await Runner.run(
        agent,
        "What city is the Golden Gate Bridge in?",
        session=session
    )
    print(result.final_output)  # "San Francisco"

    # Second turn - agent automatically remembers previous context
    result = await Runner.run(
        agent,
        "What state is it in?",
        session=session
    )
    print(result.final_output)  # "California"

    # Also works with synchronous runner
    result = Runner.run_sync(
        agent,
        "What's the population?",
        session=session
    )
    print(result.final_output)  # "Approximately 39 million"

if __name__ == "__main__":
    asyncio.run(main())