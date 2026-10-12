"""Day 3：新闻舆情分析（LLM 做情感分类 + 摘要）。

运行测试：python sentiment.py
"""
import pandas as pd

from llm import MODEL, extract_json, get_client


def analyze_sentiment(news: pd.DataFrame, stock_name: str) -> dict:
    if news.empty:
        return {"items": [], "overall": "中性", "score": 0,
                "summary": "近期没有获取到相关新闻", "key_events": []}

    lines = []
    for i, row in news.iterrows():
        content = str(row["content"])[:150].replace("\n", " ")
        lines.append(f"{i + 1}. [{row['time']}] {row['title']} —— {content}")
    news_text = "\n".join(lines)

    prompt = f"""你是一名 A 股研究员。以下是「{stock_name}」近期的新闻，请逐条判断对股价的影响，并给出整体结论。

只输出 JSON，不要输出任何其他文字，格式如下：
{{
  "items": [{{"index": 1, "sentiment": "利好|中性|利空", "reason": "一句话理由"}}],
  "overall": "利好|中性|利空",
  "score": 一个 -100 到 100 的整数（越大越利好）,
  "summary": "不超过 100 字的总结",
  "key_events": ["关键事件1", "关键事件2"]
}}

新闻列表：
{news_text}"""

    resp = get_client().chat.completions.create(
        model=MODEL, max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )
    return extract_json(resp.choices[0].message.content or "")


if __name__ == "__main__":
    import json
    from data_fetcher import get_news, get_stock_name

    code = "000001"
    result = analyze_sentiment(get_news(code), get_stock_name(code))
    print(json.dumps(result, ensure_ascii=False, indent=2))
