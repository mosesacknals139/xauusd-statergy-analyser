import MetaTrader5 as mt5
import pandas as pd

def get_data(symbol, timeframe, bars=200):

    tf_map = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "H1": mt5.TIMEFRAME_H1
    }

    rates = mt5.copy_rates_from_pos(
        symbol,
        tf_map[timeframe],
        0,
        bars
    )

    df = pd.DataFrame(rates)

    df['time'] = pd.to_datetime(df['time'], unit='s')

    return df