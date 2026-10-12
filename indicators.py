"""Day 2：技术指标计算 + 信号文字化。

全部用 pandas 手写（MA / MACD / RSI / 布林带），不依赖 pandas-ta，避免安装兼容问题。
运行测试：python indicators.py
"""
import pandas as pd


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["close"]

    # 均线
    for n in (5, 10, 20, 60):
        df[f"ma{n}"] = c.rolling(n).mean()

    # MACD（12, 26, 9）
    ema12 = c.ewm(span=12, adjust=False).mean()
    ema26 = c.ewm(span=26, adjust=False).mean()
    df["dif"] = ema12 - ema26
    df["dea"] = df["dif"].ewm(span=9, adjust=False).mean()
    df["macd"] = (df["dif"] - df["dea"]) * 2

    # RSI（14）
    delta = c.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()
    rs = avg_gain / avg_loss
    df["rsi14"] = 100 - 100 / (1 + rs)

    # 布林带（20, 2）
    mid = c.rolling(20).mean()
    std = c.rolling(20).std()
    df["boll_mid"] = mid
    df["boll_up"] = mid + 2 * std
    df["boll_low"] = mid - 2 * std
    return df


def summarize_signals(df: pd.DataFrame) -> dict:
    """把指标翻译成文字信号，供 LLM 解读（数字由代码算，LLM 不算数）。"""
    if len(df) < 60:
        raise ValueError("历史数据不足 60 个交易日，无法计算指标")

    d = add_indicators(df)
    last, prev = d.iloc[-1], d.iloc[-2]
    signals = []

    # 趋势
    if last["ma5"] > last["ma20"] > last["ma60"]:
        signals.append("均线多头排列（MA5 > MA20 > MA60），中期趋势向上")
    elif last["ma5"] < last["ma20"] < last["ma60"]:
        signals.append("均线空头排列（MA5 < MA20 < MA60），中期趋势向下")
    else:
        signals.append("均线纠缠，趋势不明朗")

    # 均线交叉
    if prev["ma5"] <= prev["ma20"] and last["ma5"] > last["ma20"]:
        signals.append("MA5 上穿 MA20（金叉）")
    elif prev["ma5"] >= prev["ma20"] and last["ma5"] < last["ma20"]:
        signals.append("MA5 下穿 MA20（死叉）")

    # MACD
    if prev["dif"] <= prev["dea"] and last["dif"] > last["dea"]:
        signals.append("MACD 金叉（DIF 上穿 DEA）")
    elif prev["dif"] >= prev["dea"] and last["dif"] < last["dea"]:
        signals.append("MACD 死叉（DIF 下穿 DEA）")
    else:
        pos = "零轴上方" if last["dif"] > 0 else "零轴下方"
        signals.append(f"MACD 位于{pos}，DIF {'高于' if last['dif'] > last['dea'] else '低于'} DEA")

    # RSI
    rsi = last["rsi14"]
    if rsi > 70:
        signals.append(f"RSI14={rsi:.1f}，进入超买区")
    elif rsi < 30:
        signals.append(f"RSI14={rsi:.1f}，进入超卖区")
    else:
        signals.append(f"RSI14={rsi:.1f}，处于中性区间")

    # 布林带
    if last["close"] > last["boll_up"]:
        signals.append("收盘价突破布林带上轨，短期偏强但有回调风险")
    elif last["close"] < last["boll_low"]:
        signals.append("收盘价跌破布林带下轨，短期偏弱但有反弹可能")
    else:
        side = "上方" if last["close"] > last["boll_mid"] else "下方"
        signals.append(f"收盘价位于布林带中轨{side}")

    # 量能
    vol_ratio = last["volume"] / d["volume"].iloc[-21:-1].mean()
    if vol_ratio > 1.5:
        signals.append(f"成交量放大（约为 20 日均量的 {vol_ratio:.1f} 倍）")
    elif vol_ratio < 0.7:
        signals.append(f"成交量萎缩（约为 20 日均量的 {vol_ratio:.1f} 倍）")

    return {
        "latest_date": str(last["date"].date()),
        "close": round(float(last["close"]), 2),
        "change_5d_pct": round(float(last["close"] / d.iloc[-6]["close"] - 1) * 100, 2),
        "change_20d_pct": round(float(last["close"] / d.iloc[-21]["close"] - 1) * 100, 2),
        "ma5": round(float(last["ma5"]), 2),
        "ma20": round(float(last["ma20"]), 2),
        "ma60": round(float(last["ma60"]), 2),
        "rsi14": round(float(rsi), 1),
        "support_20d": round(float(d["low"].iloc[-20:].min()), 2),
        "resistance_20d": round(float(d["high"].iloc[-20:].max()), 2),
        "signals": signals,
    }


if __name__ == "__main__":
    import json
    from data_fetcher import get_price_history

    prices = get_price_history("000001")
    print(json.dumps(summarize_signals(prices), ensure_ascii=False, indent=2))
