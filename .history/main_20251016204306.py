from agents import Agent, Runner, SQLiteSession, OpenAIChatCompletionsModel, set_default_openai_client,set_tracing_disabled
from openai import AsyncOpenAI
from agents.extensions.models.litellm_model import LitellmModel
import asyncio

async def main():
    # Create agent
    agent = Agent(
        name         = "Assistant",
        instructions = "Reply very concisely.",
        model= LitellmModel(model="deepseek/deepseek-chat", api_key="sk-f4605f9bf44d418895fe946cfa17dd7d")
    )

    # Create a session instance
    session = SQLiteSession("conversation_123")

    # First turn
    result = await Runner.run(
        agent,
        "What city is the Golden Gate Bridge in?",
        session = session,
    )
    print(result.final_output)  # "San Francisco"

    # Second turn - agent automatically remembers previous context
    result = await Runner.run(
        agent,
        "What state is it in?",
        session = session,
    )
    print(result.final_output)  # "California"

if __name__ == "__main__":
    asyncio.run(main())