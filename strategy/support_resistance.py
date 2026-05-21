def detect_support_resistance(df):

    resistance = df['high'].rolling(window=20).max().iloc[-1]
    support = df['low'].rolling(window=20).min().iloc[-1]

    current_price = df.iloc[-1]['close']

    breakout = None

    # BUY BREAKOUT
    if current_price > resistance:
        breakout = "BUY"

    # SELL BREAKOUT
    elif current_price < support:
        breakout = "SELL"

    return support, resistance, breakout