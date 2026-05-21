def retest_confirmation(df, resistance, support):

    last = df.iloc[-1]

    signal = None

    # BUY RETEST
    if (
        last['close'] > resistance and
        last['low'] <= resistance
    ):

        signal = "BUY"

    # SELL RETEST
    elif (
        last['close'] < support and
        last['high'] >= support
    ):

        signal = "SELL"

    return signal