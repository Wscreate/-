"""LLM 公共模块：创建 DeepSeek 客户端、解析 JSON。

运行测试：python llm.py
"""
import json
import os
import re

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError(
                "未找到 DEEPSEEK_API_KEY，请在项目根目录的 .env 中配置 DeepSeek API 密钥"
            )
        _client = OpenAI(api_key=api_key, base_url=BASE_URL)
    return _client


def extract_json(text: str) -> dict:
    """从模型输出中提取 JSON（兼容被 ```json 包裹的情况）。"""
    text = re.sub(r"```(?:json)?", "", text).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"模型输出中没有找到 JSON：{text[:200]}")
    return json.loads(text[start:end + 1])


if __name__ == "__main__":
    resp = get_client().chat.completions.create(
        model=MODEL,
        max_tokens=100,
        messages=[{"role": "user", "content": "用一句话介绍你自己"}],
    )
    print(resp.choices[0].message.content)
