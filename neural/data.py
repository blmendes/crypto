
from binance import Client 
import pandas as pd 
import time 

api_key = 'KID05KbYWa3LrNphKcKAb0WMUB0yxvxvAmFUl8hKbizG1OsDx0yfgdO5W1sGftMU'
api_secret_key = 'UrIjVv3LdQsbEEBSC34NeHt9FO12nA9YNjiPsqGWDI8077bRR7tlc7Ssd0ELtQfh'
client = Client(api_key, api_secret_key)

def get_minute_data(symbol, interval, lookback):
    df = pd.DataFrame(client.get_historical_klines(symbol,
                                                   interval,
                                                   lookback + ' min ago UTC' ))

    df = df.iloc[:,:6]
    df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index, unit = 'ms')
    df = df.astype(float)
    df['Date'] = df.index
    df.reset_index(drop=True, inplace= True)
    df.dropna(axis=1, inplace=True)
    df['Adj Close'] = df['Close']
    df['Volume'] = df['Volume'].astype(int)
    df = df[['Date', 'Open','High','Low','Close','Adj Close','Volume']]
    return df 

def get_top_symbols():
    all_pairs = pd.DataFrame(client.get_ticker())
    relev = all_pairs[all_pairs.symbol.str.contains('USDT')]
    non_lev = relev[~((relev.symbol.str.contains('UP')) | (relev.symbol.str.contains('DOWN')))]
    top_symbol = non_lev[non_lev.priceChangePercent == non_lev.priceChangePercent.max()]
    top_symbol = top_symbol.symbol.values[0]
    return top_symbol


def createframe(msg):
    df = pd.DataFrame([msg])
    df = df.loc[:,['s','E','p']]
    df.columns = ['symbol', 'Time', 'Price']
    df.Price = df.Price.astype(float)
    df.Time = pd.to_datetime(df.Time, unit = 'ms')
    return df

from binance import BinanceSocketManager
bsm = BinanceSocketManager(client)

def strategy(buy_amt, SL= 0.985, Target = 1.02, open_position =False):
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
            print(df.Close[-1])
            print(f'current Close is' + str(df.Close[-1]))
            print(f'current Target is' + str(buyprice * Target))
            print(f'current SL is' + str(buyprice * SL))

            if df.Close[-1] <= buyprice * SL or df.Close[-1] >= buyprice * Target:
                order = client.create_order(symbol=asset, side = 'SELL', type = 'MARKET', quantity=qty)
                print(order)
                break

df = get_minute_data('FISUSDT', '1m', '20')

while True:
    if df.Close[len(df.Close)-1] <= 0.86690000 * 0.985 or df.Close[len(df.Close)-1] >= 0.86690000 * 1.02:
        order = client.create_order(symbol='FISUSDT', side = 'SELL', type = 'MARKET', quantity=23)
        print(order)
    