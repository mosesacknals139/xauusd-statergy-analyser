import MetaTrader5 as mt5
from mt5.market_data import get_data
from indicators.ema import add_ema

def get_higher_timeframe_bias(source):

    if hasattr(source, "iloc"):

        df = source.copy()

    else:

        df = get_data(source, mt5.TIMEFRAME_H1)

    if "ema_50" not in df.columns or "ema_200" not in df.columns:

        df = add_ema(df)

    ema50 = df.iloc[-1]['ema_50']
    ema200 = df.iloc[-1]['ema_200']

    if ema50 > ema200:

        return "BULLISH"

    elif ema50 < ema200:

        return "BEARISH"

    return "NEUTRAL"