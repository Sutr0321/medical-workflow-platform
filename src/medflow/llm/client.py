import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def create_deepseek_client() -> OpenAI:
    """
    创建统一的 DeepSeek 客户端。

    后续整个项目都通过这里调用 DeepSeek，
    不允许其他模块重复配置 API Key 和 base_url。
    """

    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        raise RuntimeError(
            "没有读取到 DEEPSEEK_API_KEY，请检查 .env 文件"
        )

    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )