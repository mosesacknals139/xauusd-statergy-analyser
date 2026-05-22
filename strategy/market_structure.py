def detect_market_structure(df):

    bos = None
    choch = None

    highs = df['high']
    lows = df['low']

    recent_high = highs.iloc[-5:].max()
    previous_high = highs.iloc[-10:-5].max()

    recent_low = lows.iloc[-5:].min()
    previous_low = lows.iloc[-10:-5].min()

    current_close = df.iloc[-1]['close']

    # --------------------------------
    # BULLISH BOS
    # --------------------------------
    if current_close > previous_high:

        bos = "BULLISH"

    # --------------------------------
    # BEARISH BOS
    # --------------------------------
    elif current_close < previous_low:

        bos = "BEARISH"

    # --------------------------------
    # CHOCH
    # --------------------------------
    if bos == "BULLISH":

        choch = "BULLISH REVERSAL"

    elif bos == "BEARISH":

        choch = "BEARISH REVERSAL"

    return {
        "bos": bos,
        "choch": choch
    }