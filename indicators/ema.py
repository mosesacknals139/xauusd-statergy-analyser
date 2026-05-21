import ta

def add_ema(df):

    df['ema_50'] = ta.trend.EMAIndicator(
        df['close'],
        window=50
    ).ema_indicator()

    df['ema_200'] = ta.trend.EMAIndicator(
        df['close'],
        window=200
    ).ema_indicator()

    return df