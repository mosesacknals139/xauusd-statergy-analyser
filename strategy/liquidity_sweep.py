def detect_liquidity_sweep(df):

    last = df.iloc[-1]

    recent_high = df['high'].iloc[-10:-1].max()
    recent_low = df['low'].iloc[-10:-1].min()

    sweep = None

    # BUY SIDE LIQUIDITY SWEEP
    if (
        last['high'] > recent_high and
        last['close'] < recent_high
    ):

        sweep = "SELL"

    # SELL SIDE LIQUIDITY SWEEP
    elif (
        last['low'] < recent_low and
        last['close'] > recent_low
    ):

        sweep = "BUY"

    return {
        "sweep": sweep,
        "recent_high": recent_high,
        "recent_low": recent_low
    }