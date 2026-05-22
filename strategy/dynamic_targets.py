def _clean_number(value):

    try:
        if value is None:
            return None

        value = float(value)

        if value != value:
            return None

        return value
    except (TypeError, ValueError):
        return None


def _unique_sorted_levels(levels, reverse=False):

    cleaned = []

    for price, label in levels:

        price = _clean_number(price)

        if price is None:
            continue

        if all(abs(price - existing[0]) > 0.05 for existing in cleaned):
            cleaned.append((price, label))

    return sorted(cleaned, key=lambda item: item[0], reverse=reverse)


def _recent_swing_high(df, lookback=20):

    if df is None or len(df) < 3:
        return None

    window = df['high'].iloc[-lookback:-1]

    if len(window) == 0:
        return None

    return _clean_number(window.max())


def _recent_swing_low(df, lookback=20):

    if df is None or len(df) < 3:
        return None

    window = df['low'].iloc[-lookback:-1]

    if len(window) == 0:
        return None

    return _clean_number(window.min())


def _range_buffer(atr, entry):

    atr = _clean_number(atr)

    if atr is not None and atr > 0:
        return atr * 0.15

    entry = _clean_number(entry)

    if entry is None:
        return 0.0

    return entry * 0.0003


def _add_target(levels, price, label, side, entry):

    price = _clean_number(price)
    entry = _clean_number(entry)

    if price is None or entry is None:
        return

    if side == "BUY" and price > entry:
        levels.append((price, label))

    elif side == "SELL" and price < entry:
        levels.append((price, label))


def build_dynamic_trade_plan(
    side,
    entry,
    m5_df,
    m15_df=None,
    support=None,
    resistance=None,
    bullish_fvg=None,
    bearish_fvg=None,
    atr=None,
    higher_bias=None,
    trend=None
):

    entry = _clean_number(entry)

    if entry is None:
        raise ValueError("Entry price is required for dynamic trade planning")

    levels = []

    m5_high = _recent_swing_high(m5_df, lookback=20)
    m5_low = _recent_swing_low(m5_df, lookback=20)
    m15_high = _recent_swing_high(m15_df, lookback=20) if m15_df is not None else None
    m15_low = _recent_swing_low(m15_df, lookback=20) if m15_df is not None else None

    support = _clean_number(support)
    resistance = _clean_number(resistance)
    m5_high = _clean_number(m5_high)
    m5_low = _clean_number(m5_low)
    m15_high = _clean_number(m15_high)
    m15_low = _clean_number(m15_low)

    if side == "BUY":

        _add_target(levels, resistance, "Resistance liquidity", side, entry)
        _add_target(levels, m5_high, "M5 swing high liquidity", side, entry)
        _add_target(levels, m15_high, "M15 swing high liquidity", side, entry)

        if bearish_fvg is not None:

            _add_target(levels, bearish_fvg[0], "Bearish FVG fill", side, entry)

        # If there is no obvious overhead liquidity, keep a smart ATR extension as a fallback.
        if atr is not None:

            atr = _clean_number(atr)

            if atr is not None:
                _add_target(levels, entry + (atr * 1.2), "ATR fallback extension", side, entry)

        stop_candidates = [
            support,
            m5_low,
            m15_low,
        ]

        if bullish_fvg is not None:

            stop_candidates.append(bullish_fvg[0])

    elif side == "SELL":

        _add_target(levels, support, "Support liquidity", side, entry)
        _add_target(levels, m5_low, "M5 swing low liquidity", side, entry)
        _add_target(levels, m15_low, "M15 swing low liquidity", side, entry)

        if bullish_fvg is not None:

            _add_target(levels, bullish_fvg[1], "Bullish FVG fill", side, entry)

        if atr is not None:

            atr = _clean_number(atr)

            if atr is not None:
                _add_target(levels, entry - (atr * 1.2), "ATR fallback extension", side, entry)

        stop_candidates = [
            resistance,
            m5_high,
            m15_high,
        ]

        if bearish_fvg is not None:

            stop_candidates.append(bearish_fvg[1])

    else:

        raise ValueError(f"Unsupported side: {side}")

    levels = _unique_sorted_levels(levels, reverse=(side == "SELL"))

    buffer = _range_buffer(atr, entry)
    stop_candidates = [
        _clean_number(candidate)
        for candidate in stop_candidates
        if _clean_number(candidate) is not None
    ]

    if side == "BUY":

        stop_base = min(stop_candidates) if stop_candidates else entry - buffer
        stop_loss = stop_base - buffer

    else:

        stop_base = max(stop_candidates) if stop_candidates else entry + buffer
        stop_loss = stop_base + buffer

    if side == "BUY":

        if not levels:
            levels = [
                (entry + buffer * 4, "ATR fallback extension"),
                (entry + buffer * 8, "ATR fallback runner"),
                (entry + buffer * 12, "ATR fallback extension 3"),
            ]

    else:

        if not levels:
            levels = [
                (entry - buffer * 4, "ATR fallback extension"),
                (entry - buffer * 8, "ATR fallback runner"),
                (entry - buffer * 12, "ATR fallback extension 3"),
            ]

    targets = levels[:3]

    if len(targets) < 3:

        last_price = targets[-1][0] if targets else entry

        while len(targets) < 3:

            if side == "BUY":
                last_price += buffer * 4
                label = f"ATR expansion {len(targets) + 1}"
            else:
                last_price -= buffer * 4
                label = f"ATR expansion {len(targets) + 1}"

            targets.append((last_price, label))

    tp1, tp1_reason = targets[0]
    tp2, tp2_reason = targets[1]
    tp3, tp3_reason = targets[2]

    risk = abs(entry - stop_loss)

    if side == "BUY":

        rr1 = (tp1 - entry) / risk if risk else None
        rr2 = (tp2 - entry) / risk if risk else None
        rr3 = (tp3 - entry) / risk if risk else None

    else:

        rr1 = (entry - tp1) / risk if risk else None
        rr2 = (entry - tp2) / risk if risk else None
        rr3 = (entry - tp3) / risk if risk else None

    return {
        "side": side,
        "entry": entry,
        "stop_loss": stop_loss,
        "stop_reason": "Below nearest structural support" if side == "BUY" else "Above nearest structural resistance",
        "targets": [
            {"price": tp1, "label": tp1_reason, "rr": rr1},
            {"price": tp2, "label": tp2_reason, "rr": rr2},
            {"price": tp3, "label": tp3_reason, "rr": rr3},
        ],
        "higher_bias": higher_bias,
        "trend": trend,
        "risk": risk,
    }