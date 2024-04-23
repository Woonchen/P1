#查價，只有當下數據，速度較快
import time
import requests
import json
from bs4 import BeautifulSoup



init_timestamp = time.time()
for i in range(60):
    # 定义要爬取的目标网页的 URL
    url = 'https://api.binance.com/api/v1/ticker/price?symbol=ETHUSDT'

    # 发送 HTTP 请求获取网页内容
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    data_obj = json.loads(str(soup))
    price = data_obj['price']
    print(price)

    current_timestamp = time.time()
    print("間隔時間", round(current_timestamp-init_timestamp, 2))
    init_timestamp = current_timestamp



