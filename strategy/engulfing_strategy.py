def check_engulfing(df):

    last = df.iloc[-1]
    prev = df.iloc[-2]

    signal = None
    confidence = 0

    bullish_engulfing = (
        prev['close'] < prev['open'] and
        last['close'] > last['open'] and
        last['close'] > prev['open'] and
        last['open'] < prev['close']
    )

    bearish_engulfing = (
        prev['close'] > prev['open'] and
        last['close'] < last['open'] and
        last['open'] > prev['close'] and
        last['close'] < prev['open']
    )

    # BUY
    if (
        last['ema_50'] > last['ema_200'] and
        last['rsi'] < 40 and
        bullish_engulfing
    ):

        signal = "BUY"
        confidence = 85

    # SELL
    elif (
        last['ema_50'] < last['ema_200'] and
        last['rsi'] > 60 and
        bearish_engulfing
    ):

        signal = "SELL"
        confidence = 85

    return signal, confidence