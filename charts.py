"""Day 2：K 线图（红涨绿跌，符合 A 股习惯）。

运行测试：python charts.py   （会在浏览器打开图表）
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def make_kline(df, title: str = "") -> go.Figure:
    """df 需要先经过 indicators.add_indicators 处理。"""
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.6, 0.2, 0.2], vertical_spacing=0.03,
    )

    # 主图：K 线 + 均线 + 布林带
    fig.add_trace(go.Candlestick(
        x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"],
        increasing_line_color="red", decreasing_line_color="green", name="K线",
    ), row=1, col=1)
    for n in (5, 20, 60):
        fig.add_trace(go.Scatter(x=df["date"], y=df[f"ma{n}"], name=f"MA{n}",
                                 line=dict(width=1)), row=1, col=1)
    for col, name in (("boll_up", "布林上轨"), ("boll_low", "布林下轨")):
        fig.add_trace(go.Scatter(x=df["date"], y=df[col], name=name,
                                 line=dict(width=1, dash="dot", color="gray")), row=1, col=1)

    # MACD
    colors = ["red" if v >= 0 else "green" for v in df["macd"].fillna(0)]
    fig.add_trace(go.Bar(x=df["date"], y=df["macd"], marker_color=colors, name="MACD柱"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["dif"], name="DIF", line=dict(width=1)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["dea"], name="DEA", line=dict(width=1)), row=2, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df["date"], y=df["rsi14"], name="RSI14"), row=3, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="gray", row=3, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="gray", row=3, col=1)

    fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])  # 去掉周末空档
    fig.update_layout(
        title=title, height=720, xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", y=1.02),
    )
    return fig


if __name__ == "__main__":
    from data_fetcher import get_price_history
    from indicators import add_indicators

    data = add_indicators(get_price_history("000001"))
    make_kline(data, "000001 日K").show()
