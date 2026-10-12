# A 股智能分析 Agent

一个基于 Streamlit、AKShare 和 DeepSeek 的 A 股技术面分析工具。输入 6 位股票代码后，项目会获取历史行情、计算常用技术指标，并由 DeepSeek Agent 生成技术面、舆情面、综合判断和风险提示报告。

> 本项目仅供学习和研究使用，不构成投资建议。

## 功能

- 获取 A 股最近约 250 个交易日的日线行情
- 使用前复权数据计算价格趋势
- 计算 MA5/10/20/60、MACD、RSI14 和布林带
- 生成 K 线图及技术指标数据
- 通过 DeepSeek tool calls 自动调用技术分析工具
- 输出 Markdown 格式的分析报告
- 对缺少 API 密钥、行情获取失败等情况给出错误提示

## 数据源与模型

- 行情和股票名称：新浪财经，通过 AKShare 的 `stock_zh_a_daily` 和 `stock_zh_a_spot` 获取
- 新闻：当前版本不调用东方财富，也没有接入新浪个股新闻接口，因此新闻数据为空，舆情部分会按“近期没有相关新闻”处理
- 大语言模型：DeepSeek，使用 OpenAI 兼容接口

## 项目结构

```text
app.py              Streamlit 页面入口
agent.py            Agent 循环和工具调用
llm.py              DeepSeek 客户端及 JSON 解析
data_fetcher.py     新浪行情、股票名称和数据清洗
indicators.py       技术指标计算及信号总结
charts.py           K 线图绘制
sentiment.py        新闻情感分析逻辑
requirements.txt    Python 依赖
test.py             网络连接测试脚本
```

## 环境要求

- Python 3.11 或更高版本
- 可访问新浪财经数据接口
- DeepSeek API 密钥

## 安装

在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

如果 PowerShell 禁止执行虚拟环境脚本，可以直接使用虚拟环境中的 Python：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 配置 API 密钥

在项目根目录创建 `.env` 文件：

```env
DEEPSEEK_API_KEY=你的DeepSeek_API密钥
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

`.env` 已被 `.gitignore` 排除，不要将真实密钥提交到 GitHub。

## 运行

### 启动 Web 应用

```powershell
streamlit run app.py
```

浏览器打开 Streamlit 显示的本地地址，输入股票代码，例如：

```text
000001
```

### 单独测试 DeepSeek

```powershell
python llm.py
```

### 单独测试行情数据

```powershell
python data_fetcher.py
```

### 测试技术指标

```powershell
python indicators.py
```

## 分析流程

```text
输入股票代码
    ↓
新浪获取股票名称和历史行情
    ↓
计算均线、MACD、RSI、布林带等指标
    ↓
DeepSeek 请求技术分析工具和舆情工具
    ↓
执行工具并把结果返回给模型
    ↓
生成 Markdown 分析报告
```

Agent 要求模型先调用工具，再根据工具结果生成报告；报告中的技术指标由 Python 计算，避免由模型自行编造数字。

## 代理与网络

`data_fetcher.py` 会将新浪相关域名加入 `NO_PROXY`，尝试让新浪数据直连；DeepSeek API 不受该设置影响。

如果使用 Clash：

1. 检查 Clash 是否开启了 TUN 模式或系统代理；
2. 确认新浪域名使用 `DIRECT` 规则；
3. 如果 Python 环境继承了错误代理，清除 `HTTP_PROXY`、`HTTPS_PROXY` 和 `ALL_PROXY` 后重启 PyCharm。

## 注意事项

- 新浪接口可能限流或暂时封禁 IP，代码内置了有限次数的重试。
- 新浪历史接口大量请求时可能不稳定，建议避免短时间批量调用。
- 行情不足 60 个交易日时，无法计算完整的技术指标。
- 新闻接口尚未接入，因此当前报告的舆情结论不代表真实新闻分析结果。
- AI 生成的内容可能存在错误，请勿据此直接进行投资决策。

## License

本项目暂未指定开源许可证。
