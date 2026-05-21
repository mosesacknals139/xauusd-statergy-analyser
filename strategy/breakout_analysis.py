def analyze_breakout(df):

    resistance = df['high'].rolling(window=20).max().iloc[-2]
    support = df['low'].rolling(window=20).min().iloc[-2]

    current_price = df.iloc[-1]['close']

    trend = "SIDEWAYS"

    # Trend Detection
    if df.iloc[-1]['ema_50'] > df.iloc[-1]['ema_200']:
        trend = "BULLISH"

    elif df.iloc[-1]['ema_50'] < df.iloc[-1]['ema_200']:
        trend = "BEARISH"

    distance_to_resistance = resistance - current_price
    distance_to_support = current_price - support

    breakout_side = None

    # Near Resistance
    if distance_to_resistance <= 3:
        breakout_side = "BUY"

    # Near Support
    elif distance_to_support <= 3:
        breakout_side = "SELL"

    return {
        "support": support,
        "resistance": resistance,
        "current_price": current_price,
        "trend": trend,
        "breakout_side": breakout_side
    }