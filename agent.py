"""Day 4：Agent 核心 —— 用 DeepSeek tool calls 让模型决定调用哪些工具。

运行测试：python agent.py
"""
import json

from data_fetcher import get_news, get_price_history, get_stock_name
from indicators import summarize_signals
from llm import MODEL, get_client
from sentiment import analyze_sentiment

SYSTEM_PROMPT = """你是一名严谨的 A 股分析助手。
规则：
1. 必须先调用工具获取数据，再下结论；技术分析和舆情两个工具都要调用。
2. 报告中的所有数字只能来自工具返回结果，严禁编造。
3. 不要给出具体买卖价位承诺，只给"偏多 / 中性 / 偏空"的倾向和理由。

最终报告用 Markdown，结构如下：
## 一、技术面
## 二、舆情面
## 三、综合判断（偏多/中性/偏空 + 置信度高/中/低 + 核心理由）
## 四、主要风险
末尾加一行：> 本报告由 AI 生成，仅供学习参考，不构成投资建议。"""

# ---- 工具定义（告诉 LLM 有哪些工具可用）----
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_technical_analysis",
            "description": "获取 A 股个股的技术面分析：最新价、涨跌幅、均线、RSI、支撑压力位及文字化信号。",
            "parameters": {
                "type": "object",
                "properties": {"symbol": {"type": "string", "description": "6 位 A 股代码，如 000001"}},
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_news_sentiment",
            "description": "获取 A 股个股近期新闻，并返回逐条情感判断、整体舆情评分、摘要和关键事件。",
            "parameters": {
                "type": "object",
                "properties": {"symbol": {"type": "string", "description": "6 位 A 股代码，如 000001"}},
                "required": ["symbol"],
            },
        },
    },
]


# ---- 工具的真实实现 ----
def get_technical_analysis(symbol: str) -> dict:
    return summarize_signals(get_price_history(symbol))


def get_news_sentiment(symbol: str) -> dict:
    return analyze_sentiment(get_news(symbol), get_stock_name(symbol))


TOOL_FUNCS = {
    "get_technical_analysis": get_technical_analysis,
    "get_news_sentiment": get_news_sentiment,
}


def run_agent(query: str, on_step=None, max_turns: int = 8) -> str:
    """Agent 循环：模型请求工具 → 我们执行 → 结果喂回模型 → 直到模型给出最终回答。"""
    client = get_client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]

    for _ in range(max_turns):
        resp = client.chat.completions.create(
            model=MODEL, max_tokens=2000, tools=TOOLS,
            tool_choice="auto", messages=messages,
        )
        message = resp.choices[0].message

        if not message.tool_calls:  # 没有再要工具，说明是最终回答
            return message.content or ""

        assistant_message = {
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in message.tool_calls
            ],
        }
        messages.append(assistant_message)

        for call in message.tool_calls:
            name = call.function.name
            if on_step:
                on_step(f"🔧 调用工具：{name}({call.function.arguments})")
            try:
                arguments = json.loads(call.function.arguments or "{}")
                output = TOOL_FUNCS[name](**arguments)
                content = json.dumps(output, ensure_ascii=False, default=str)
            except Exception as e:  # 工具失败也要告诉模型，让它如实说明
                content = f"工具执行失败：{e}"
                if on_step:
                    on_step(f"⚠️ {content}")
            messages.append({
                "role": "tool", "tool_call_id": call.id, "content": content,
            })

    return "分析步骤过多，已中止，请重试。"


if __name__ == "__main__":
    print(run_agent("请分析 A 股平安银行（代码 000001）", on_step=print))
