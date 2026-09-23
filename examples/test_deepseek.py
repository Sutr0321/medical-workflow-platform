import os

from dotenv import load_dotenv
from openai import OpenAI


# 读取项目根目录下的 .env
load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise RuntimeError(
        "没有读取到 DEEPSEEK_API_KEY，请检查项目根目录下的 .env 文件"
    )


client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",
)


response = client.chat.completions.create(
    model="deepseek-flash",
    messages=[
        {
            "role": "system",
            "content": "你是医学数据分析工作流平台中的AI辅助模块。"
        },
        {
            "role": "user",
            "content": "请只回复：DeepSeek API 调用成功"
        }
    ],
    stream=False,
)


print(response.choices[0].message.content)