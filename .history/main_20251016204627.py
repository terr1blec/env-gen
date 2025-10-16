from agents import Agent, Runner, SQLiteSession, OpenAIChatCompletionsModel, set_default_openai_client,set_tracing_disabled
from openai import AsyncOpenAI
from agents.extensions.models.litellm_model import LitellmModel
import asyncio

agent = Agent(
    name         = "Assistant",
    instructions = "Reply very concisely.",
    model= LitellmModel(model="deepseek/deepseek-chat", api_key="sk-f4605f9bf44d418895fe946cfa17dd7d")
)

spanish_agent = Agent(
    name         = "Spanish agent",
    instructions = "You only speak Spanish.",
    model= LitellmModel(model="deepseek/deepseek-chat", api_key="sk-f4605f9bf44d418895fe946cfa17dd7d")
)

english_agent = Agent(
    name         = "English agent",
    instructions = "You only speak English",
    model        = LitellmModel(model="deepseek/deepseek-chat", api_key="sk-f4605f9bf44d418895fe946cfa17dd7d")
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
)

async def main():
    result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
    print(result.final_output)
    # ¡Hola! Estoy bien, gracias por preguntar. ¿Y tú, cómo estás?


if __name__ == "__main__":
    asyncio.run(main())