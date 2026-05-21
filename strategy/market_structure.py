def detect_market_structure(df):

    highs = df['high']
    lows = df['low']

    recent_high = highs.iloc[-2]
    previous_high = highs.iloc[-5:-2].max()

    recent_low = lows.iloc[-2]
    previous_low = lows.iloc[-5:-2].min()

    bos = None
    choch = None

    # Bullish BOS
    if recent_high > previous_high:
        bos = "BULLISH"

    # Bearish BOS
    elif recent_low < previous_low:
        bos = "BEARISH"

    # CHOCH Detection
    last_close = df.iloc[-1]['close']

    ema50 = df.iloc[-1]['ema_50']
    ema200 = df.iloc[-1]['ema_200']

    # Bullish CHOCH
    if ema50 < ema200 and recent_high > previous_high:
        choch = "BULLISH REVERSAL"

    # Bearish CHOCH
    elif ema50 > ema200 and recent_low < previous_low:
        choch = "BEARISH REVERSAL"

    return {
        "bos": bos,
        "choch": choch,
        "recent_high": recent_high,
        "recent_low": recent_low
    }