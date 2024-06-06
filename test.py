#策略回測
#各種策略各開一個檔案
#目前RSI策略超爛 需要加上KD在測試
import matplotlib.pyplot as plt
from binance.um_futures import UMFutures
import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, ADXIndicator
from ta.volatility import BollingerBands
from time import sleep
from line_notify import line_Notify


from key import api, secret

api = api
secret = secret
client = UMFutures(key = api, secret=secret)
symbol = 'ETHUSDT'

#interval: 1m 3m 5m 15m 30m 1h 2h 4h 6h 8h 12h 1d 3d 1w 1m
def klines(symbol):
    resp = pd.DataFrame(client.klines(symbol, '3m', limit = 500))
    resp = resp.iloc[:,:6]
    resp.columns = ['Time', 'Open', 'High', 'Low', 'Price', 'Volume']
    resp = resp.set_index('Time')
    resp.index = pd.to_datetime(resp.index, unit = 'ms')
    resp = resp.astype(float)
    resp.drop(['Open', 'High', 'Low', 'Volume'], axis=1, inplace=True)
    return resp

def sma100_20_7(symbol):        #適合搭配長線 30m以上
    resp = klines(symbol)
    resp['MA7'] = resp['Price'].rolling(window=7).mean()
    resp['MA20'] = resp['Price'].rolling(window=20).mean()
    resp['MA100'] = resp['Price'].rolling(window=100).mean()
    resp['std'] = resp['Price'].rolling(window=20).std()
    resp['Signal'] = 0  # 先将所有元素初始化为 0
    resp['pos_account'] = 0

    #0.price 1.MA7 2.MA20 3.MA100 4.std 5.signal 6.pos_account
    for i in range(1, len(resp)):  
        #if (resp.iat[i-1, 1] < resp.iat[i-1, 3]) and (resp.iat[i-1, 2] < resp.iat[i-1, 3]) and (resp.iat[i, 1] > resp.iat[i, 3]) and (resp.iat[i-1, 6] == 0):
        if (resp.iat[i-1, 0] < resp.iat[i-1, 3]) and (resp.iat[i, 0] < resp.iat[i, 3]) and (resp.iat[i-1, 6] == 0):
            resp.iat[i, 5] = 1   #buy
            resp.iat[i, 6] = resp.iat[i-1, 6] + 1
        elif (resp.iat[i-1, 1] > resp.iat[i-1, 2]) and (resp.iat[i, 1] < resp.iat[i, 2]) and (resp.iat[i-1, 6] > 0):
            resp.iat[i, 5] = -1  #sell
            resp.iat[i, 6] = resp.iat[i-1, 6] - 1
        else:
            resp.iat[i, 6]  = resp.iat[i-1, 6]
    resp.drop(['std'], axis=1, inplace=True)
    resp.to_excel('SMA_output.xlsx')
    return resp

def bband(symbol):
    resp = klines(symbol)
    resp['bband_mid'] = resp['Price'].rolling(window=20).mean() 
    resp['bband_up'] = resp['Price'].rolling(window=20).mean() + 2*resp['Price'].rolling(window=20).std()
    resp['bband_down'] = resp['Price'].rolling(window=20).mean() - 2*resp['Price'].rolling(window=20).std()
    resp['std'] = resp['Price'].rolling(window=20).std()
    resp['Signal'] = 0  
    resp['pos_account'] = 0
 
    loc_upper = None
    loc_lower = None
    #resp.to_excel('bband_output.xlsx')
    #print(type(resp.iat[2, 6]))

    #0.price 1.mid 2.up 3.down 4.std 5.signal 6.pos_account
    for i in range(1, len(resp)):
        try: 
            #if resp.iat[i, 4] > max(resp.iat[i-1, 4], resp.iat[i-2, 4], resp.iat[i-3, 4], resp.iat[i-4, 4], resp.iat[i-5, 4]) and resp.iat[i, 0] > resp.iat[i, 1] and (resp.iat[i-1, 6] == 0):
            if (resp.iat[i-1, 0] < resp.iat[i-1, 2]) and (resp.iat[i, 0] > resp.iat[i, 2]) and (resp.iat[i-1, 6] == 0):
                resp.iat[i, 5] = 1   #buy
                resp.iat[i, 6] = resp.iat[i-1, 6] + 1
            #elif (loc_upper-resp.iat[i, 2])*(loc_lower-resp.iat[i, 3])<0 and (resp.iat[i, 0] < resp.iat[i, 2]) and (resp.iat[i-1, 6] > 0):
            elif (resp.iat[i-1, 0] > resp.iat[i-1, 1]) and (resp.iat[i, 0] < resp.iat[i, 1]) and (resp.iat[i-1, 6] > 0):
                resp.iat[i, 5] = -1  #sell
                resp.iat[i, 6] = resp.iat[i-1, 6] - 1
                loc_upper = None
                loc_lower = None
            else:
                resp.iat[i, 6]  = resp.iat[i-1, 6]
        except:
            None

        if (resp.iat[i, 6] > 0):
            if loc_upper == None or loc_upper < resp.iat[i, 2]:
                loc_upper = resp.iat[i, 2]
            if loc_lower == None or loc_lower > resp.iat[i, 3]:
                loc_lower = resp.iat[i, 3]

    # #0.price 1.mid 2.up 3.down 4.std 5.signal 6.pos_account
    # for i in range(1, len(resp)):  
    #     if (resp.iat[i-1, 0] < resp.iat[i-1, 3]) and (resp.iat[i, 0] > resp.iat[i, 3]) and (resp.iat[i-1, 6] == 0):
    #         resp.iat[i, 5] = 1   #buy
    #         resp.iat[i, 6] = resp.iat[i-1, 6] + 1
    #     elif (resp.iat[i-1, 0] > resp.iat[i-1, 2]) and (resp.iat[i, 0] < resp.iat[i, 2]) and (resp.iat[i-1, 6] > 0):
    #         resp.iat[i, 5] = -1  #sell
    #         resp.iat[i, 6] = resp.iat[i-1, 6] - 1
    #     else:
    #         resp.iat[i, 6]  = resp.iat[i-1, 6]
    resp.drop(['std'], axis=1, inplace=True)
    resp.to_excel('bband_output.xlsx')
    return resp

def RSI(symbol):
    resp = klines(symbol)
    resp['RSI7'] = RSIIndicator(resp['Price'], window=7).rsi()
    resp['RSI14'] = RSIIndicator(resp['Price'], window=14).rsi()
    # resp['K'] = StochasticOscillator(resp['High'], resp['Low'], resp['Price'], window=14).stoch()
    # resp['D'] = SMAIndicator(resp['K'], window=14).sma_indicator()
    resp['none'] = 0 
    resp['Signal'] = 0  
    resp['pos_account'] = 0
    

    #resp.to_excel('RSI_output.xlsx')

    # #0.price 1.rsi7 2.rsi14 3.none 4.signal 5.pos_account 6.money
    for i in range(1, len(resp)):
        try: 
            if (resp.iat[i-1, 1] < resp.iat[i-1, 2]) and (resp.iat[i, 1] > resp.iat[i, 2]) and (resp.iat[i-1, 5] == 0):
                resp.iat[i, 4] = 1   #buy
                resp.iat[i, 5] = resp.iat[i-1, 5] + 1
            elif (resp.iat[i-1, 1] > resp.iat[i-1, 2]) and (resp.iat[i, 1] < resp.iat[i, 2]) and (resp.iat[i-1, 5] > 0):
                resp.iat[i, 4] = -1  #sell
                resp.iat[i, 5] = resp.iat[i-1, 5] - 1
            else:
                resp.iat[i, 5]  = resp.iat[i-1, 5]
        except:
            None

    resp.to_excel('RSI_output.xlsx')
    return resp

def plot(resp):
    # #0.price 1.mid 2.up 3.down 4.signal 5.pos_account 6.money
    #圖2  資產變化
    ax3 = plt.subplot(313)
    resp['money'] = money       #money為第7行
    for i in range(1, len(resp)):
        if (resp.iat[i, 4]==1):     #買入時
            resp.iat[i, 6] = resp.iat[i-1, 6] - resp.iat[i, 0]*unit*multiple*0.0005
        elif(resp.iat[i, 4]==-1):    #賣出時
            resp.iat[i, 6] = resp.iat[i-1, 6] + (resp.iat[i, 0] - resp.iat[i-1, 0])*unit*multiple - resp.iat[i, 0]*unit*multiple*0.0005
        elif(resp.iat[i, 4]==0):
            if (resp.iat[i, 5]==1):     #持倉時
                resp.iat[i, 6] = resp.iat[i-1, 6] + (resp.iat[i, 0] - resp.iat[i-1, 0])*unit*multiple
            if (resp.iat[i, 5]==0):     #無倉位時
                resp.iat[i, 6] = resp.iat[i-1, 6]     
    resp[['money']].plot(ax=ax3)
    ax3.set_ylabel('Money')
    resp.drop(['money'], axis=1, inplace=True)



    #圖1  價格變化和策略指標
    ax1 = plt.subplot(311, sharex=ax3)
    #  買賣點
    buy_df = resp[resp['Signal']>0]  #買入點
    sell_df = resp[resp['Signal']<0]  #賣出點
    
    resp.drop(['Signal', 'pos_account'], axis=1, inplace=True)
    
    #resp.to_excel('output123.xlsx')  

    resp[['Price']].plot(ax=ax1, color = 'black')   #標示價格變化   
    #標示買賣點
    ax1.scatter(buy_df.index,buy_df[['Price']]-15,marker='^',s=100, c='red', label='')
    ax1.scatter(sell_df.index,sell_df[['Price']]+15,marker='v',s=100, c='green', label='',)
    ax1.set_ylabel('Price')
    try:
        resp.drop(['Price', 'none'], axis=1, inplace=True)
    except:
        resp.drop(['Price'], axis=1, inplace=True)
    

    ax2 = plt.subplot(312, sharex=ax3)
    resp.plot(ax=ax2)   #標示resp所有資料(策略指標)


    
    # #绘制折线图
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


#資產設置
money = 20
unit = 0.001
multiple = 10

#交易策略
#resp = sma100_20_7(symbol)
#resp = bband(symbol)
resp = RSI(symbol)
#print(resp.iloc[-1])
plot(resp)
#line_Notify('111')




