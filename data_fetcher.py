"""Day 1：数据采集（行情 + 新闻）。

运行测试：python data_fetcher.py
"""
import os
import time

# 新浪数据源直连，不走系统代理 / VPN 代理。
# 访问 DeepSeek API 等其他服务不受影响。
_DIRECT = ["sina.com.cn", "sinajs.cn"]
_no_proxy = [h for h in os.environ.get("NO_PROXY", "").split(",") if h]
os.environ["NO_PROXY"] = ",".join(_no_proxy + [d for d in _DIRECT if d not in _no_proxy])
os.environ["no_proxy"] = os.environ["NO_PROXY"]

import akshare as ak  # noqa: E402  (必须在设置 NO_PROXY 之后导入)
import pandas as pd  # noqa: E402

def _retry(func, *args, retries: int = 3, delay: float = 1.5, **kwargs):
    """失败自动重试（接口偶尔会被限流或断连）。"""
    last_err = None
    for i in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_err = e
            time.sleep(delay * (i + 1))
    raise last_err


def _with_prefix(symbol: str) -> str:
    """新浪接口需要带交易所前缀：sh / sz / bj。"""
    if symbol.startswith(("6", "900")):
        return "sh" + symbol
    if symbol.startswith(("4", "8", "92")):
        return "bj" + symbol
    return "sz" + symbol


def get_price_history(symbol: str, days: int = 250) -> pd.DataFrame:
    """通过新浪获取 A 股日线行情（前复权），返回最近 days 个交易日。"""
    today = pd.Timestamp.today()
    start = (today - pd.Timedelta(days=int(days * 1.6))).strftime("%Y%m%d")
    end = today.strftime("%Y%m%d")

    df = _retry(
        ak.stock_zh_a_daily,
        symbol=_with_prefix(symbol),
        start_date=start, end_date=end, adjust="qfq",
    )  # 新浪接口返回英文列名：date/open/high/low/close/volume/amount...

    if df is None or df.empty:
        raise ValueError(f"没有获取到 {symbol} 的行情，请检查股票代码")

    df["date"] = pd.to_datetime(df["date"])
    return df.tail(days).reset_index(drop=True)


_NAME_CACHE: dict = {}


def get_stock_name(symbol: str) -> str:
    """通过新浪 A 股实时行情表获取股票简称，失败则返回代码本身。"""
    if symbol in _NAME_CACHE:
        return _NAME_CACHE[symbol]

    try:
        table = _retry(ak.stock_zh_a_spot, retries=2)
        codes = table["代码"].astype(str).str.zfill(6)
        hit = table.loc[codes == symbol, "名称"]
        name = str(hit.iloc[0]) if not hit.empty else symbol
    except Exception as e:
        print(f"[data] 新浪取名称失败：{type(e).__name__}: {str(e)[:80]}")
        name = symbol
    _NAME_CACHE[symbol] = name
    return name


def get_news(symbol: str, limit: int = 10) -> pd.DataFrame:
    """返回个股新闻表。

    当前 AkShare 没有新浪个股新闻接口。为保证项目完全不访问东方财富，
    暂时返回空结果；上层情感分析会将其处理为“近期没有相关新闻”。
    """
    return pd.DataFrame(columns=["time", "title", "content", "source", "url"])


if __name__ == "__main__":
    code = "000001"
    print("股票名称：", get_stock_name(code))
    prices = get_price_history(code)
    print(prices.tail())
    print(f"共 {len(prices)} 个交易日")
    print(get_news(code)[["time", "title"]])
