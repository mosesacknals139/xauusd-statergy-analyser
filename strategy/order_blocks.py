def detect_order_block(df):

    last_candles = df.iloc[-10:]

    bullish_ob = None
    bearish_ob = None

    for i in range(len(last_candles) - 1):

        current = last_candles.iloc[i]
        next_candle = last_candles.iloc[i + 1]

        # Bullish Order Block
        if (
            current['close'] < current['open']
            and next_candle['close'] > next_candle['open']
            and next_candle['close'] > current['high']
        ):

            bullish_ob = current['low']

        # Bearish Order Block
        elif (
            current['close'] > current['open']
            and next_candle['close'] < next_candle['open']
            and next_candle['close'] < current['low']
        ):

            bearish_ob = current['high']

    return {
        "bullish_ob": bullish_ob,
        "bearish_ob": bearish_ob
    }