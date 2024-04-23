#現貨交易
#Bband策略

import ccxt
import time
#import sys
# import json
#import pandas as np
#import winsound
import saveToExcel
from datetime import datetime
from time import sleep
from key import api, secret


# 連接到 Binance 交易所
binance = ccxt.binance({
    'apiKey': api,
    'secret': secret,
    'enableRateLimit': True,
})

# 交易對和時間間隔
symbol = 'ETH/USDT'
timeframe = '3m'


# 交易策略-布林帶
def strategy_BBand(history_data, ready_to_buy, ready_to_sell, pos_amount, price_buy, last_upper, last_lower):
    latest_data = history_data[-1:][0][4]

    sum = 0
    for data in history_data[-20:]:
        sum += data[4]
    middle_vals = sum/20 #20MA
    
    sum = 0
    for data in history_data[-20:]:
        sum += (data[4]-middle_vals)**2
    std = (sum/20)**0.5
    upper_vals =middle_vals+2*std #bband upper value
    lower_vals =middle_vals-2*std #bband lower value
    #print('upper_vals: {:.2f}, middle_vals: {:.2f}, lower_vals: {:.2f}'.format(upper_vals, middle_vals, lower_vals))
    #print(latest_data)
    #print(ready_to_buy, ready_to_sell, pos_amount)

    if pos_amount >0 : #有倉位
        if (std < max_std) and (latest_data < middle_vals) and (ready_to_buy == 1): #通道收縮，價格低於MA20賣出
            signal = 'sell'
        elif (std >= max_std) and (latest_data > upper_vals): #通道打開，價格高於上通道，準備賣出
            signal = 'ready_to_sell'
        else:
            signal = '持倉中'   
        
    elif pos_amount == 0: #沒有倉位
        if (std >= max_std) and (latest_data > middle_vals): #通道收縮，價格高於MA20購買
            signal = 'buy'          
        elif (last_std == min_std) and (std > last_std): #通道收縮後打開
            signal = 'ready_to_buy'
        else:
            signal = '等待中'
    
    else :
        signal = 'None'
    
    return (signal, latest_data, std, upper_vals, lower_vals)

# 自動交易


ready_to_buy = 0
ready_to_sell = 0
pos_amount = 0

last_std = -10
max_std = 0
min_std = 999
last_upper = 0
last_lower = 0


price_buy = None
price_sell = None
time_buy = None
ratio = None
trade_usdt = 5.01
amount =None

print('bband start')
print('--------------------')
while True:
    try:
        # 獲取歷史數據
        history_data = binance.fetch_ohlcv(symbol, timeframe, limit=100)
        #print(json.dumps(history_data,indent=4)) 
        # 判斷交易信號
        signal = strategy_BBand(history_data, ready_to_buy, ready_to_sell, pos_amount, price_buy, last_upper, last_lower) 
        #print(signal)

        # 获取当前时间
        current_time = datetime.now()
        # 格式化当前时间
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # 執行交易
        if signal[0] == 'buy':
            ready_to_buy = 0
            pos_amount += 1
            price_buy = round(signal[1], 2)
            amount = round(trade_usdt/price_buy, 2)
            max_std = 0
            min_std = 999
            #binance.create_market_buy_order(symbol, amount)  # 以市價買入amount個以太幣
            saveToExcel.saveToExcel(formatted_time, price_buy, "-", "-", "-")
            #winsound.Beep(1000, 300)  # 参数：频率（Hz），持续时间（毫秒）
            print('買入信號', price_buy)

        elif signal[0] == 'sell':
            #binance.create_market_sell_order(symbol, amount)  # 以市價賣出amount個以太幣
            ready_to_sell = 0
            pos_amount -= 1
            price_sell = round(signal[1], 2)
            ratio = round((price_sell - price_buy)/price_buy, 5)
            max_std = 0
            min_std = 999
            saveToExcel.saveToExcel(formatted_time, price_buy, price_sell, ratio, 'bband')
            #winsound.Beep(1000, 300)  # 参数：频率（Hz），持续时间（毫秒)
            sleep(0.3)
            #winsound.Beep(1000, 300)  # 参数：频率（Hz），持续时间（毫秒）
            print('賣出信號', price_sell)
            print('價差: ', round(price_sell - price_buy, 5))
            print('百分比: ', ratio, ' %')
            print('--------------------')

            

        elif signal[0] == 'ready_to_buy':
            ready_to_buy = 1
            #print('ready_to_buy')
        elif signal[0] == 'ready_to_sell':
            ready_to_sell = 1
            #print('ready_to_sell')
        elif signal[0] == '持倉中':
            #print('持倉中')
            None
        elif signal[0] == '等待中':
            #print('等待中')
            None


        
        last_upper = signal[3]
        last_lower = signal[4]
        last_std = signal[2]
        if max_std < signal[2]:
            max_std = signal[2]
        if min_std > signal[2]:
            min_std = signal[2]

        # 等待下一次交易
        time.sleep(1)  # 等待秒數

    except Exception as e:
        print('發生異常:', e)