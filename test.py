# author: Barry
# 2024年09月23日10时46分51秒
# email:2990670974@qq.com

import requests
import json
import urllib3

# API URL
url = "http://192.168.102.101:8000/save_config"
# 请求头
headers = {
    "Content-Type": "application/json"
}

# 请求体 (根据需要替换实际的查询条件)
payload = {
    "ip":"192.168.102.151",
    "port":"8000"
}

# 发送 POST 请求
response = requests.post(url, headers=headers, data=json.dumps(payload))

# 检查响应状态码
if response.status_code == 200:
    # 输出响应的JSON内容
    data = response.json()
    print("请求成功:", data)
else:
    # 输出错误信息
    print(f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}")
