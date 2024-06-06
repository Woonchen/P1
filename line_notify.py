import requests

url = 'https://notify-api.line.me/api/notify'
token = 'MxljRXbaiWAJWSjBhOoGVB903iY4VwkyzjemJ53dTNP'
headers = {
    'Authorization': 'Bearer ' + token    # 設定權杖
}

def line_Notify(Messenger):
    data = {
        'message': str(Messenger)     # 設定要發送的訊息
    }
    data = requests.post(url, headers=headers, data=data)   # 使用 POST 方法

