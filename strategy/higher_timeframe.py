from mt5.market_data import get_data
from indicators.ema import add_ema

import MetaTrader5 as mt5

def get_higher_timeframe_bias(symbol):

    df = get_data(symbol, mt5.TIMEFRAME_M15)

    df = add_ema(df)

    ema50 = df.iloc[-1]['ema_50']
    ema200 = df.iloc[-1]['ema_200']

    if ema50 > ema200:

        return "BULLISH"

    elif ema50 < ema200:

        return "BEARISH"

    return "NEUTRAL"