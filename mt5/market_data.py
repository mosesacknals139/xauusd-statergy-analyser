import MetaTrader5 as mt5
import pandas as pd

def get_data(symbol, timeframe, bars=200):

    tf_map = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "H1": mt5.TIMEFRAME_H1
    }

    # Accept either a string key (e.g. "M5") or a numeric mt5.TIMEFRAME_* value
    if isinstance(timeframe, str):
        tf = tf_map[timeframe]
    else:
        tf = timeframe

    rates = mt5.copy_rates_from_pos(
        symbol,
        tf,
        0,
        bars
    )

    df = pd.DataFrame(rates)

    df['time'] = pd.to_datetime(df['time'], unit='s')

    return df