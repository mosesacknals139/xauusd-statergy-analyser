def _candle_body(candle):

    return abs(candle['close'] - candle['open'])


def _upper_wick(candle):

    return candle['high'] - max(candle['open'], candle['close'])


def _lower_wick(candle):

    return min(candle['open'], candle['close']) - candle['low']


def _safe_recent_high(df, lookback=6):

    window = df['high'].iloc[-lookback:-1]

    if len(window) == 0:
        return df['high'].max()

    return window.max()


def _safe_recent_low(df, lookback=6):

    window = df['low'].iloc[-lookback:-1]

    if len(window) == 0:
        return df['low'].min()

    return window.min()


def get_m1_sniper_entry(df, side, support=None, resistance=None, higher_bias=None):

    result = {
        "confirmed": False,
        "side": side,
        "score": 0,
        "trigger": None,
        "entry_price": None,
        "stop_loss": None,
        "atr": None,
        "micro_bias": None,
        "reasons": []
    }

    if df is None or len(df) < 40:

        result["reasons"].append("Not enough M1 candles for sniper confirmation")
        return result

    # Use the last closed candle for confirmation to avoid reacting to a candle still forming.
    last = df.iloc[-2]
    prev = df.iloc[-3]
    current = df.iloc[-1]

    atr = last.get("atr")
    if atr is not None and atr == atr:
        result["atr"] = float(atr)

    ema50 = last.get("ema_50")
    ema200 = last.get("ema_200")
    rsi = last.get("rsi")

    body = _candle_body(last)
    candle_range = last['high'] - last['low']
    upper_wick = _upper_wick(last)
    lower_wick = _lower_wick(last)
    body_ratio = (body / candle_range) if candle_range > 0 else 0
    recent_high = _safe_recent_high(df, lookback=8)
    recent_low = _safe_recent_low(df, lookback=8)

    if ema50 == ema50 and ema200 == ema200:

        if ema50 > ema200:
            result["micro_bias"] = "BULLISH"
        elif ema50 < ema200:
            result["micro_bias"] = "BEARISH"

    score = 0
    trigger_found = None
    reasons = []

    if side == "BUY":

        if higher_bias == "BULLISH":
            score += 2
            reasons.append("H1 bias aligned bullish")

        if result["micro_bias"] == "BULLISH":
            score += 2
            reasons.append("M1 micro bias bullish")

        if ema50 == ema50 and last['close'] > ema50:
            score += 1
            reasons.append("Price above M1 EMA50")

        if ema200 == ema200 and last['close'] > ema200:
            score += 1
            reasons.append("Price above M1 EMA200")

        if support is not None and last['low'] <= support <= last['close']:
            score += 2
            trigger_found = "support reclaim"
            reasons.append("Support reclaimed on M1")

        if last['low'] < recent_low and last['close'] > recent_low:
            score += 2
            trigger_found = trigger_found or "liquidity sweep reclaim"
            reasons.append("M1 sweep and reclaim")

        if last['close'] > prev['high'] and last['close'] > recent_high:
            score += 1
            trigger_found = trigger_found or "micro breakout"
            reasons.append("M1 break above prior high")

        if last['close'] > last['open'] and lower_wick >= max(body * 1.0, candle_range * 0.2):
            score += 1
            trigger_found = trigger_found or "rejection candle"
            reasons.append("Bullish rejection candle")

        if rsi == rsi and 50 <= rsi <= 68:
            score += 1
            reasons.append("RSI in bullish sniper zone")

        if candle_range > 0 and (last['close'] - last['low']) / candle_range >= 0.7:
            score += 1
            reasons.append("Strong close near candle high")

        if body_ratio >= 0.45:
            score += 1
            reasons.append("Strong bullish candle body")

        sl_anchor = min(last['low'], support if support is not None else last['low'])

    elif side == "SELL":

        if higher_bias == "BEARISH":
            score += 2
            reasons.append("H1 bias aligned bearish")

        if result["micro_bias"] == "BEARISH":
            score += 2
            reasons.append("M1 micro bias bearish")

        if ema50 == ema50 and last['close'] < ema50:
            score += 1
            reasons.append("Price below M1 EMA50")

        if ema200 == ema200 and last['close'] < ema200:
            score += 1
            reasons.append("Price below M1 EMA200")

        if resistance is not None and last['high'] >= resistance >= last['close']:
            score += 2
            trigger_found = "resistance rejection"
            reasons.append("Resistance rejected on M1")

        if last['high'] > recent_high and last['close'] < recent_high:
            score += 2
            trigger_found = trigger_found or "liquidity sweep rejection"
            reasons.append("M1 sweep and reject")

        if last['close'] < prev['low'] and last['close'] < recent_low:
            score += 1
            trigger_found = trigger_found or "micro breakdown"
            reasons.append("M1 break below prior low")

        if last['close'] < last['open'] and upper_wick >= max(body * 1.0, candle_range * 0.2):
            score += 1
            trigger_found = trigger_found or "rejection candle"
            reasons.append("Bearish rejection candle")

        if rsi == rsi and 32 <= rsi <= 50:
            score += 1
            reasons.append("RSI in bearish sniper zone")

        if candle_range > 0 and (last['high'] - last['close']) / candle_range >= 0.7:
            score += 1
            reasons.append("Strong close near candle low")

        if body_ratio >= 0.45:
            score += 1
            reasons.append("Strong bearish candle body")

        sl_anchor = max(last['high'], resistance if resistance is not None else last['high'])

    else:

        result["reasons"].append(f"Unsupported side: {side}")
        return result

    buffer = result["atr"] * 0.15 if result["atr"] is not None else 0.0

    if side == "BUY":
        stop_loss = sl_anchor - buffer
    else:
        stop_loss = sl_anchor + buffer

    result["score"] = score
    result["trigger"] = trigger_found
    result["stop_loss"] = stop_loss
    result["reasons"] = reasons

    confirmed = score >= 8 and trigger_found is not None

    if confirmed:
        result["confirmed"] = True
        result["entry_price"] = float(last['close'])

    # If the live candle is already invalidating the idea, keep the result unconfirmed.
    if side == "BUY" and current['close'] < current['open'] and current['low'] < last['low']:
        result["confirmed"] = False
        result["reasons"].append("Live candle still weak for buy")

    if side == "SELL" and current['close'] > current['open'] and current['high'] > last['high']:
        result["confirmed"] = False
        result["reasons"].append("Live candle still weak for sell")

    return result


def build_m1_pre_entry_alert(side, support=None, resistance=None, higher_bias=None, m1_trigger=None):

    if side == "BUY":

        break_level = resistance
        invalidation_level = support
        break_text = "If M1 closes above resistance, we can take the buy entry."
        watch_text = "Waiting for breakout confirmation above resistance."

    elif side == "SELL":

        break_level = support
        invalidation_level = resistance
        break_text = "If M1 closes below support, we can take the sell entry."
        watch_text = "Waiting for breakdown confirmation below support."

    else:

        break_level = None
        invalidation_level = None
        break_text = "Waiting for valid direction."
        watch_text = "No M1 watch condition available."

    trigger_name = None
    score = None
    reasons = []

    if m1_trigger:

        trigger_name = m1_trigger.get("trigger")
        score = m1_trigger.get("score")
        reasons = m1_trigger.get("reasons") or []

    message = [
        "⏳ M1 PRE-ENTRY WATCH",
        "",
        f"Direction → {side}",
        f"Higher TF Bias → {higher_bias}",
        f"Watch Level → {break_level}",
        f"Invalidation → {invalidation_level}",
        f"M1 Trigger → {trigger_name}",
        f"M1 Score → {score}",
        "",
        watch_text,
        break_text,
    ]

    if reasons:
        message.append("")
        message.append("Why it is close:")
        message.extend(f"• {reason}" for reason in reasons[:5])

    return "\n".join(str(line) for line in message)