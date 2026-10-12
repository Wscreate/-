"""Day 5：Streamlit 界面。

运行：streamlit run app.py
"""
import streamlit as st

from agent import run_agent
from charts import make_kline
from data_fetcher import get_price_history, get_stock_name
from indicators import add_indicators

st.set_page_config(page_title="A股智能分析 Agent", layout="wide")
st.title("📈 A股智能分析 Agent")
st.caption("仅供学习参考，不构成投资建议")


@st.cache_data(ttl=600)
def load_price(symbol: str):
    return add_indicators(get_price_history(symbol))


symbol = st.text_input("股票代码（6 位，如 000001）", "000001").strip()

if st.button("开始分析", type="primary"):
    if not (symbol.isdigit() and len(symbol) == 6):
        st.error("请输入 6 位数字的 A 股代码")
        st.stop()

    try:
        name = get_stock_name(symbol)
        st.subheader(f"{name}（{symbol}）")
        with st.spinner("加载行情..."):
            df = load_price(symbol)
        st.plotly_chart(make_kline(df, f"{name} 日K"))
    except Exception as e:
        st.error(f"行情获取失败：{e}")
        st.stop()

    with st.status("Agent 分析中...", expanded=True) as status:
        try:
            report = run_agent(
                f"请分析 A 股 {name}（代码 {symbol}），给出技术面、舆情面和综合判断。",
                on_step=lambda s: st.write(s),
            )
            status.update(label="分析完成", state="complete")
        except Exception as e:
            status.update(label="分析失败", state="error")
            st.error(f"Agent 运行出错：{e}")
            st.stop()

    st.markdown(report)
