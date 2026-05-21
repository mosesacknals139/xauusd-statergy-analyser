def detect_fvg(df):

    bullish_fvg = None
    bearish_fvg = None

    for i in range(2, len(df)):

        candle1 = df.iloc[i - 2]
        candle2 = df.iloc[i - 1]
        candle3 = df.iloc[i]

        # Bullish FVG
        if candle1['high'] < candle3['low']:

            bullish_fvg = (
                candle1['high'],
                candle3['low']
            )

        # Bearish FVG
        elif candle1['low'] > candle3['high']:

            bearish_fvg = (
                candle3['high'],
                candle1['low']
            )

    return {
        "bullish_fvg": bullish_fvg,
        "bearish_fvg": bearish_fvg
    }