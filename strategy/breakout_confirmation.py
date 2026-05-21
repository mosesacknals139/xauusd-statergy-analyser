def confirm_breakout(df, resistance, support):

    current_price = df.iloc[-1]['close']

    # BUY breakout
    if current_price > resistance:
        return "BUY"

    # SELL breakout
    elif current_price < support:
        return "SELL"

    return None