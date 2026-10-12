import requests

url = "https://finance.sina.com.cn/"

try:
    print("默认(走系统代理):", requests.get(url, timeout=10).status_code)
except Exception as e:
    print("默认(走系统代理): 失败", type(e).__name__)

s = requests.Session()
s.trust_env = False  # 忽略系统代理
try:
    print("强制直连:", s.get(url, timeout=10).status_code)
except Exception as e:
    print("强制直连: 失败", type(e).__name__)
