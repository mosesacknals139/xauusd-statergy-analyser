def calculate_confidence(
    signal,
    bos,
    sweep,
    bullish_ob,
    bearish_ob,
    bullish_fvg,
    bearish_fvg,
    trend
):

    confidence = 0

    # --------------------------------
    # BOS
    # --------------------------------
    if signal == "BUY" and bos == "BULLISH":
        confidence += 20

    elif signal == "SELL" and bos == "BEARISH":
        confidence += 20

    # --------------------------------
    # LIQUIDITY SWEEP
    # --------------------------------
    if signal == "BUY" and sweep == "BUY":
        confidence += 20

    elif signal == "SELL" and sweep == "SELL":
        confidence += 20

    # --------------------------------
    # ORDER BLOCK
    # --------------------------------
    if signal == "BUY" and bullish_ob:
        confidence += 15

    elif signal == "SELL" and bearish_ob:
        confidence += 15

    # --------------------------------
    # FAIR VALUE GAP
    # --------------------------------
    if signal == "BUY" and bullish_fvg:
        confidence += 15

    elif signal == "SELL" and bearish_fvg:
        confidence += 15

    # --------------------------------
    # TREND ALIGNMENT
    # --------------------------------
    if signal == "BUY" and trend == "BULLISH":
        confidence += 10

    elif signal == "SELL" and trend == "BEARISH":
        confidence += 10

    # --------------------------------
    # RETEST BONUS
    # --------------------------------
    confidence += 10

    # --------------------------------
    # SESSION BONUS
    # --------------------------------
    confidence += 10

    return confidence