import ta

def add_rsi(df):

    df['rsi'] = ta.momentum.RSIIndicator(
        df['close'],
        window=14
    ).rsi()

    return df