def build_market_update(state: dict) -> str:
    """Build a professional market commentary message from `state`.

    Expected keys in `state` (all optional, but helpful):
      - symbol (str)
      - timeframe_bias (str) e.g. 'H1: Bearish'
      - price (float)
      - reaction_zone (str)
      - liquidity (str)
      - invalidation (str)
      - confirmations (list of str)
      - waiting_for (list of str)
      - expectations (list of str)
      - session (str)
      - notes (str)
      - entry_status (str) e.g. 'No entry — waiting for confirmation'

    Returns a plain-text multi-line commentary string suitable for Telegram.
    """

    s = state.get
    symbol = s("symbol", "XAUUSD")
    timeframe_bias = s("timeframe_bias", "H1 bias: Neutral")
    price = s("price")
    reaction_zone = s("reaction_zone")
    liquidity = s("liquidity")
    invalidation = s("invalidation")
    confirmations = s("confirmations", [])
    waiting_for = s("waiting_for", [])
    expectations = s("expectations", [])
    session = s("session")
    notes = s("notes")
    entry_status = s("entry_status", "No entry — waiting for confirmation")

    lines = []
    lines.append("━━━━━━━━━━━━━━━━━━")
    lines.append(f"📊 {symbol} MARKET UPDATE")
    lines.append("━━━━━━━━━━━━━━━━━━")
    if session:
        lines.append(f"🕒 Session → {session}")
    lines.append(f"🧭 {timeframe_bias}")
    if price is not None:
        lines.append(f"📍 Price → {price}")

    if reaction_zone:
        lines.append("")
        lines.append("🔁 Reaction Zone")
        lines.append(f"→ {reaction_zone}")

    if liquidity:
        lines.append("")
        lines.append("💧 Liquidity")
        lines.append(f"→ {liquidity}")

    if invalidation:
        lines.append("")
        lines.append("❌ Invalidation")
        lines.append(f"→ {invalidation}")

    if confirmations:
        lines.append("")
        lines.append("✅ What Confirms")
        for c in confirmations:
            lines.append(f"→ {c}")

    if waiting_for:
        lines.append("")
        lines.append("🔎 Waiting For")
        for w in waiting_for:
            lines.append(f"→ {w}")

    if expectations:
        lines.append("")
        lines.append("📈 Expectations / Scenarios")
        for e in expectations:
            lines.append(f"→ {e}")

    lines.append("")
    lines.append("📌 Trade Status")
    lines.append(f"→ {entry_status}")

    if notes:
        lines.append("")
        lines.append("📝 Notes")
        lines.append(notes)

    lines.append("━━━━━━━━━━━━━━━━━━")

    return "\n".join(lines)

def example_payload():
    return {
        "symbol": "XAUUSD",
        "timeframe_bias": "H1 Bias → Bearish",
        "price": 4520.35,
        "reaction_zone": "M15 bearish order block 4520.00-4522.00",
        "liquidity": "Buy-side liquidity at 4514.20",
        "invalidation": "Close above 4526.00 invalidates bearish bias",
        "confirmations": ["M1 bearish engulfing", "M5 close below 4514.80"],
        "waiting_for": ["M1 engulfing", "M5 structural close"],
        "expectations": ["If rejects at 4520 → continuation to 4508 liquidity"],
        "session": "London Open",
        "notes": "No entry yet — watch for micro-confirmation before scaling in.",
        "entry_status": "Watching — no active entry"
    }


def _sparkline(series):
    """Create a tiny unicode sparkline from a list of numbers."""
    if not series:
        return ""
    ticks = "▁▂▃▄▅▆▇█"
    mn = min(series)
    mx = max(series)
    if mx == mn:
        return ticks[0] * len(series)
    out = []
    for v in series:
        idx = int((v - mn) / (mx - mn) * (len(ticks) - 1))
        out.append(ticks[idx])
    return "".join(out)


def build_market_update_html(state: dict) -> str:
    """Build an HTML-formatted market update for Telegram `parse_mode='HTML'`.

    Accepts same keys as `build_market_update`. Optional `price_series` can
    be provided (list of floats) to render a small sparkline.
    """

    s = state.get
    symbol = s("symbol", "XAUUSD")
    timeframe_bias = s("timeframe_bias", "H1 bias: Neutral")
    price = s("price")
    reaction_zone = s("reaction_zone")
    liquidity = s("liquidity")
    invalidation = s("invalidation")
    confirmations = s("confirmations", [])
    waiting_for = s("waiting_for", [])
    expectations = s("expectations", [])
    session = s("session")
    notes = s("notes")
    entry_status = s("entry_status", "No entry — waiting for confirmation")
    price_series = s("price_series", [])

    parts = []
    parts.append("━━━━━━━━━━━━━━━━━━")
    parts.append(f"<b>📊 {symbol} MARKET UPDATE</b>")
    parts.append("━━━━━━━━━━━━━━━━━━")
    if session:
        parts.append(f"<i>🕒 Session → {session}</i>")
    parts.append(f"<b>🧭 {timeframe_bias}</b>")
    if price is not None:
        parts.append(f"📍 Price → <b>{price:.2f}</b>")

    if price_series:
        spark = _sparkline(price_series)
        parts.append(f"<pre>{spark}  {price_series[-1]:.2f}</pre>")

    if reaction_zone:
        parts.append(f"\n<b>🔁 Reaction Zone</b>\n→ {reaction_zone}")

    if liquidity:
        parts.append(f"\n<b>💧 Liquidity</b>\n→ {liquidity}")

    if invalidation:
        parts.append(f"\n<b>❌ Invalidation</b>\n→ {invalidation}")

    if confirmations:
        parts.append("\n<b>✅ What Confirms</b>")
        for c in confirmations:
            parts.append(f"→ {c}")

    if waiting_for:
        parts.append("\n<b>🔎 Waiting For</b>")
        for w in waiting_for:
            parts.append(f"→ {w}")

    if expectations:
        parts.append("\n<b>📈 Expectations / Scenarios</b>")
        for e in expectations:
            parts.append(f"→ {e}")

    parts.append("\n<b>📌 Trade Status</b>")
    parts.append(f"→ {entry_status}")

    if notes:
        parts.append("\n<b>📝 Notes</b>")
        parts.append(notes)

    parts.append("━━━━━━━━━━━━━━━━━━")

    return "\n".join(parts)


def state_has_meaningful_change(prev: dict, curr: dict) -> (bool, list):
    """Return (changed:bool, reasons:list) comparing two state dicts.

    Triggers considered meaningful:
      - timeframe bias flip
      - reaction_zone change
      - liquidity change/sweep
      - BOS/CHOCH change
    """

    if prev is None:
        return True, ["initial"]

    reasons = []

    if prev.get("timeframe_bias") != curr.get("timeframe_bias"):
        reasons.append("bias_flip")

    if prev.get("reaction_zone") != curr.get("reaction_zone"):
        reasons.append("reaction_zone")

    if prev.get("liquidity") != curr.get("liquidity"):
        reasons.append("liquidity")

    if prev.get("bos") != curr.get("bos"):
        reasons.append("bos")

    if prev.get("choch") != curr.get("choch"):
        reasons.append("choch")

    return (len(reasons) > 0), reasons


def _distance_to_level(price, level):
    if price is None or level is None:
        return None
    try:
        return abs(float(price) - float(level))
    except (TypeError, ValueError):
        return None


def detect_market_events(curr: dict, prev: dict | None = None) -> list[str]:
    """Detect market events worth narrating."""

    events = []

    price = curr.get("price")
    support = curr.get("support")
    resistance = curr.get("resistance")
    bullish_ob = curr.get("bullish_ob")
    bearish_ob = curr.get("bearish_ob")
    bullish_fvg = curr.get("bullish_fvg")
    bearish_fvg = curr.get("bearish_fvg")
    sweep = curr.get("sweep")
    bos = curr.get("bos")
    choch = curr.get("choch")

    if prev:
        if prev.get("timeframe_bias") != curr.get("timeframe_bias"):
            events.append("Bias flip detected")
        if prev.get("bos") != bos and bos:
            events.append(f"Structure break confirmed ({bos})")
        if prev.get("choch") != choch and choch:
            events.append(f"CHOCH confirmed ({choch})")
        if prev.get("sweep") != sweep and sweep:
            events.append(f"Liquidity sweep confirmed ({sweep})")

    # Approaching levels: if price is near the zone, narrate it.
    level_checks = [
        ("bullish OB", bullish_ob),
        ("bearish OB", bearish_ob),
    ]
    for label, level in level_checks:
        distance = _distance_to_level(price, level)
        if distance is not None and distance <= max(0.35, (price * 0.00008)):
            events.append(f"Price approaching {label} at {float(level):.2f}")

    fvg_checks = [
        ("bullish FVG", bullish_fvg),
        ("bearish FVG", bearish_fvg),
    ]
    for label, level in fvg_checks:
        if isinstance(level, (tuple, list)) and len(level) == 2 and price is not None:
            low, high = float(level[0]), float(level[1])
            if low <= float(price) <= high:
                events.append(f"Price inside {label} {low:.2f}-{high:.2f}")
            else:
                dist = min(abs(float(price) - low), abs(float(price) - high))
                if dist <= max(0.35, (price * 0.00008)):
                    events.append(f"Price approaching {label} {low:.2f}-{high:.2f}")

    if support is not None and price is not None:
        dist = abs(float(price) - float(support))
        if dist <= max(0.4, (price * 0.0001)):
            events.append(f"Price approaching support {float(support):.2f}")

    if resistance is not None and price is not None:
        dist = abs(float(price) - float(resistance))
        if dist <= max(0.4, (price * 0.0001)):
            events.append(f"Price approaching resistance {float(resistance):.2f}")

    return list(dict.fromkeys(events))


def build_market_narrative(curr: dict, prev: dict | None = None) -> str:
    """Build a short narrative that preserves the story from one update to the next."""

    symbol = curr.get("symbol", "XAUUSD")
    timeframe_bias = curr.get("timeframe_bias", "H1 bias: Neutral")
    price = curr.get("price")
    reaction_zone = curr.get("reaction_zone")
    liquidity = curr.get("liquidity")
    invalidation = curr.get("invalidation")
    entry_status = curr.get("entry_status", "No entry — waiting for confirmation")

    parts = [f"📊 {symbol} MARKET COMMENTARY"]

    if prev and prev.get("timeframe_bias") != timeframe_bias:
        parts.append(f"Bias changed from {prev.get('timeframe_bias')} to {timeframe_bias}.")
    else:
        parts.append(f"{timeframe_bias} remains the working bias.")

    if reaction_zone:
        parts.append(f"Price is reacting near {reaction_zone}.")

    if liquidity:
        parts.append(f"Liquidity focus: {liquidity}.")

    if invalidation:
        parts.append(f"Invalidation level: {invalidation}.")

    if price is not None:
        parts.append(f"Spot price: {float(price):.2f}.")

    parts.append(entry_status + ".")

    return " ".join(parts)


def build_commentary_payload(curr: dict, prev: dict | None = None) -> dict:
    """Create a richer commentary payload from market state and market memory."""

    events = detect_market_events(curr, prev)
    confirmations = curr.get("confirmations") or []
    waiting_for = curr.get("waiting_for") or []
    expectations = curr.get("expectations") or []

    if events:
        expectations = list(dict.fromkeys(events + expectations))

    narrative = build_market_narrative(curr, prev)

    return {
        "symbol": curr.get("symbol", "XAUUSD"),
        "timeframe_bias": curr.get("timeframe_bias", "H1 bias: Neutral"),
        "price": curr.get("price"),
        "reaction_zone": curr.get("reaction_zone"),
        "liquidity": curr.get("liquidity"),
        "invalidation": curr.get("invalidation"),
        "confirmations": confirmations,
        "waiting_for": waiting_for,
        "expectations": expectations,
        "session": curr.get("session"),
        "notes": narrative,
        "entry_status": curr.get("entry_status", "No entry — waiting for confirmation"),
        "price_series": curr.get("price_series", []),
        "events": events,
        "market_memory": {
            "previous_bias": prev.get("timeframe_bias") if prev else None,
            "previous_reaction_zone": prev.get("reaction_zone") if prev else None,
            "previous_invalidation": prev.get("invalidation") if prev else None,
        },
        "bos": curr.get("bos"),
        "choch": curr.get("choch"),
        "support": curr.get("support"),
        "resistance": curr.get("resistance"),
        "sweep": curr.get("sweep"),
        "bullish_ob": curr.get("bullish_ob"),
        "bearish_ob": curr.get("bearish_ob"),
        "bullish_fvg": curr.get("bullish_fvg"),
        "bearish_fvg": curr.get("bearish_fvg"),
    }

