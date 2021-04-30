import pandas as pd

def get_data(symbol, timeframe):
    # http://www.cryptodatadownload.com/data/
    # timeframe must be {'d', '1h', 'minute'}
    url = f'http://www.cryptodatadownload.com/cdd/Binance_{symbol.upper()}USDT_{timeframe}.csv'
    return pd.read_csv(url, skiprows=1)