from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
import asyncio

# 创建模型实例（只创建一次）
deepseek_model = LitellmModel(model="deepseek/deepseek-chat", api_key="sk-f4605f9bf44d418895fe946cfa17dd7d")

# 创建各个agent
spanish_agent = Agent(
    name         = "Spanish agent",
    instructions = "You only speak Spanish.",
    model= deepseek_model
)

english_agent = Agent(
    name         = "English agent",
    instructions = "You only speak English",
    model        = deepseek_model
)

triage_agent = Agent(
    name         = "Triage agent",
    instructions = "Handoff to the appropriate agent based on the language of the request.",
    handoffs     = [spanish_agent, english_agent],
    model        = deepseek_model  # 使用同一个模型实例
)

async def main():
    try:
        result = await Runner.run(triage_agent, input="Hola, ¿cómo estás?")
        print(result.final_output)
        # ¡Hola! Estoy bien, gracias por preguntar. ¿Y tú, cómo estás?
    except Exception as e:
        print(f"发生错误: {e}")
        print("请检查:")
        print("1. API密钥是否正确")
        print("2. 网络连接是否正常")
        print("3. 模型名称是否正确")

if __name__ == "__main__":
    asyncio.run(main())