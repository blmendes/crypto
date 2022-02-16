from data import get_top_symbols, get_minute_data
import time
from binance import Client 

api_key = 'KID05KbYWa3LrNphKcKAb0WMUB0yxvxvAmFUl8hKbizG1OsDx0yfgdO5W1sGftMU'
api_secret_key = 'UrIjVv3LdQsbEEBSC34NeHt9FO12nA9YNjiPsqGWDI8077bRR7tlc7Ssd0ELtQfh'
client = Client(api_key, api_secret_key)

from binance import BinanceSocketManager
bsm = BinanceSocketManager(client)

def strategy(buy_amt, SL= 0.975, Target = 1.035, open_position =False):
    #validar tendencia e potencial de crescimento deve ser maior que o TP 
    #validar padrão de candlesticks
    try:
        asset = get_top_symbols()
        df = get_minute_data(asset, '1m', '120')
    except:
        time.sleep(61)
        asset = get_top_symbols()
        df = get_minute_data(asset, '1m', '120')
    
    qty = round(buy_amt/df.Close.iloc[-1])

    if ((df.Close.pct_change()+2).cumprod()).iloc[-1] > 1:
        order = client.create_order(symbol=asset, side = 'BUY', type = 'MARKET', quantity=qty)
        print(order)
        buyprice = float(order['fills'][0]['price'])
        open_position = True
        while open_position:
            try:
                df = get_minute_data(asset, '1m', '2')
            except:
                print('Something wrong')
                time.sleep(61)
                df = get_minute_data(asset, '1m', '2')

            print(f'current Close is' + str(df.Close[len(df.Close)-1]))
            print(f'current Target is' + str(buyprice * Target))
            print(f'current SL is' + str(buyprice * SL))

            if df.Close[len(df.Close)-1] <= buyprice * SL or df.Close[len(df.Close)-1] >= buyprice * Target:
                order = client.create_order(symbol=asset, side = 'SELL', type = 'MARKET', quantity=qty)
                print(order)
                break

print(get_top_symbols())
df = get_minute_data(get_top_symbols(), '1m', '20')

while True:
    strategy(20)