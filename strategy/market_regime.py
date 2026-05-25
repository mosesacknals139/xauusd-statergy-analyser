def _normalize_bias(value):
    if value is None:
        return None
    text = str(value).upper()
    if "BULL" in text:
        return "BULLISH"
    if "BEAR" in text:
        return "BEARISH"
    if "SIDE" in text or "RANGE" in text:
        return "RANGING"
    return text


def classify_market_regime(
    higher_bias=None,
    m15_trend=None,
    bos=None,
    choch=None,
    sweep=None,
    support=None,
    resistance=None,
    price=None,
):
    """Classify the current market environment.

    Returns a dict with:
      - regime: TRENDING_BULLISH / TRENDING_BEARISH / REVERSAL / RANGE / TRANSITION
      - bias_alignment: FULL / PARTIAL / MISALIGNED
      - bullish_allowed: bool
      - bearish_allowed: bool
      - reversal_confirmed: bool
      - summary: short explanation
    """

    h1 = _normalize_bias(higher_bias)
    m15 = _normalize_bias(m15_trend)
    bos_n = _normalize_bias(bos)
    choch_n = _normalize_bias(choch)
    sweep_n = _normalize_bias(sweep)

    bullish_stack = h1 == "BULLISH" and m15 == "BULLISH"
    bearish_stack = h1 == "BEARISH" and m15 == "BEARISH"

    reversal_confirmed = False

    if choch_n == "BULLISH REVERSAL" and bos_n == "BULLISH":
        reversal_confirmed = True
    elif choch_n == "BEARISH REVERSAL" and bos_n == "BEARISH":
        reversal_confirmed = True
    elif sweep_n == "BUY" and bos_n == "BULLISH":
        reversal_confirmed = True
    elif sweep_n == "SELL" and bos_n == "BEARISH":
        reversal_confirmed = True

    regime = "TRANSITION"
    bias_alignment = "MISALIGNED"
    bullish_allowed = True
    bearish_allowed = True

    if bullish_stack:
        regime = "TRENDING_BULLISH"
        bias_alignment = "FULL"
        bullish_allowed = True
        bearish_allowed = reversal_confirmed
    elif bearish_stack:
        regime = "TRENDING_BEARISH"
        bias_alignment = "FULL"
        bullish_allowed = reversal_confirmed
        bearish_allowed = True
    elif h1 == m15 and h1 in ("BULLISH", "BEARISH"):
        regime = "TRENDING_" + h1
        bias_alignment = "PARTIAL"
        bullish_allowed = h1 == "BULLISH" or reversal_confirmed
        bearish_allowed = h1 == "BEARISH" or reversal_confirmed
    elif choch_n:
        regime = "REVERSAL"
        bias_alignment = "MISALIGNED"
        bullish_allowed = choch_n == "BULLISH REVERSAL" or reversal_confirmed
        bearish_allowed = choch_n == "BEARISH REVERSAL" or reversal_confirmed
    else:
        regime = "RANGE"
        bias_alignment = "MISALIGNED"
        bullish_allowed = True
        bearish_allowed = True

    if price is not None and support is not None and resistance is not None:
        try:
            price = float(price)
            support = float(support)
            resistance = float(resistance)
            if abs(price - support) <= abs(resistance - support) * 0.12:
                summary = f"Price is near support at {support:.2f}."
            elif abs(price - resistance) <= abs(resistance - support) * 0.12:
                summary = f"Price is near resistance at {resistance:.2f}."
            else:
                summary = f"Price is trading inside the active range {support:.2f}-{resistance:.2f}."
        except (TypeError, ValueError):
            summary = f"Market regime classified as {regime}."
    else:
        summary = f"Market regime classified as {regime}."

    return {
        "regime": regime,
        "bias_alignment": bias_alignment,
        "bullish_allowed": bullish_allowed,
        "bearish_allowed": bearish_allowed,
        "reversal_confirmed": reversal_confirmed,
        "summary": summary,
        "higher_bias": h1,
        "m15_trend": m15,
        "bos": bos_n,
        "choch": choch_n,
        "sweep": sweep_n,
    }


def direction_allowed(regime_info, signal_side):
    side = str(signal_side).upper()
    if side == "BUY":
        return bool(regime_info.get("bullish_allowed")), regime_info.get("regime", "UNKNOWN")
    if side == "SELL":
        return bool(regime_info.get("bearish_allowed")), regime_info.get("regime", "UNKNOWN")
    return False, regime_info.get("regime", "UNKNOWN")
