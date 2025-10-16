from agents import Agent, Runner, SQLiteSession, OpenAIChatCompletionsModel, set_default_openai_client,set_tracing_disabled
from openai import AsyncOpenAI
from agents.extensions.models.litellm_model import LitellmModel
import asyncio

set_tracing_disabled(disabled=True)
deepseek_model = LitellmModel(model="deepseek/deepseek-chat", api_key="sk-f4605f9bf44d418895fe946cfa17dd7d")
from agents import Agent, Runner, function_tool

  # 定义文件操作函数
@function_tool
def read_file(path: str) -> str: 
    """读取给定路径文件的文本内容"""
         try                                   : 
    with open(path, "r", encoding="utf-8") as f: 
            return f.read()
    except Exception as e: 
        return f"Error reading file: {e}"

@function_tool
def write_file(path: str, content: str) -> str: 
    """把 content 写入 path（覆盖模式）"""
         try                                   : 
    with open(path, "w", encoding="utf-8") as f: 
            f.write(content)
        return f"Written to {path}"
    except Exception as e: 
        return f"Error writing file: {e}"

@function_tool
def list_dir(path: str) -> str: 
    """列出 path 目录下的内容（文件和子目录）"""
    import os
    try: 
        items = os.listdir(path)
        return "\n".join(items)
    except Exception as e:
        return f"Error listing dir: {e}"

@function_tool
def make_dir(path: str) -> str:
    """创建一个目录（如果不存在）"""
    import os
    try:
        os.makedirs(path, exist_ok=True)
        return f"Directory created (or already exists): {path}"
    except Exception as e:
        return f"Error making dir: {e}"

@function_tool
def delete_file(path: str) -> str:
    """删除指定文件"""
    import os
    try:
        os.remove(path)
        return f"Deleted file: {path}"
    except Exception as e:
        return f"Error deleting file: {e}"

# 构造 Agent，注入这些工具
agent = Agent(
    name="FileAgent",
    instructions="你可以帮助用户管理本地文件系统，比如读写、创建、删除目录和文件",
    tools=[read_file, write_file, list_dir, make_dir, delete_file],
)

# 使用 Runner 启动
import asyncio

async def main():
    # 例如：写一个文件，然后读它
    res = await Runner.run(agent, "请在当前目录下创建一个文件 test.txt，写入 “Hello, world” 然后读取内容")
    print("Agent final output:", res.final_output)

if __name__ == "__main__":
    asyncio.run(main())
