# -*- coding: utf-8 -*-
import sys
import requests

# 目标页面 URL
url = 'http://tonkiang.us/hoteliptv.php'

# 从命令行参数中获取搜索关键字
if len(sys.argv) < 2:
    print("Usage: python test.py <search_keyword>")
    sys.exit(1)

keyword = sys.argv[1]

# 构造 POST 请求参数
payload = {'search': keyword}

# 发送 POST 请求
response = requests.post(url, data=payload)

# 打印响应内容
print(response.text)
