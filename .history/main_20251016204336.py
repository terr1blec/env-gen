from agents import Agent, Runner, SQLiteSession, OpenAIChatCompletionsModel, set_default_openai_client,set_tracing_disabled
from openai import AsyncOpenAI
from agents.extensions.models.litellm_model import LitellmModel

agent = Agent(
    name         = "Assistant",
    instructions = "Reply very concisely.",
    model= LitellmModel(model="deepseek/deepseek-chat", api_key="sk-f4605f9bf44d418895fe946cfa17dd7d")
)
