from html import escape


def _fmt_price(value):

    if value is None:
        return "N/A"

    return f"{float(value):.2f}"


def _fmt_pct(value):

    if value is None:
        return "N/A"

    return f"{int(round(float(value)))}%"


def _fmt_reason(value):

    if value is None:
        return "N/A"

    return escape(str(value))


def _setup_grade(confidence):

    if confidence is None:
        return "UNRATED"

    confidence = float(confidence)

    if confidence >= 90:
        return "A+"
    if confidence >= 80:
        return "A"
    if confidence >= 70:
        return "B+"
    if confidence >= 60:
        return "B"
    return "C"


def _format_target_rows(targets):

    lines = []

    for index, target in enumerate(targets, start=1):

        if not target:
            continue

        price = _fmt_price(target.get("price"))
        label = _fmt_reason(target.get("label"))
        rr = target.get("rr")

        if rr is None:
            rr_text = "N/A"
        else:
            rr_text = f"{float(rr):.2f}R"

        lines.append(f"🎯 TP{index} → {price} <i>({label}, {rr_text})</i>")

    return "\n".join(lines)


def _format_lines(items):

    return "\n".join(items)


def build_premium_setup_message(
    symbol,
    side,
    higher_bias=None,
    m15_bos=None,
    choch=None,
    liquidity=None,
    order_block=None,
    fvg=None,
    entry_low=None,
    entry_high=None,
    stop_loss=None,
    targets=None,
    confidence=None,
    session=None,
    wait_note=None,
    market_narrative=None,
    setup_reason=None,
    trade_plan=None,
    trigger_note=None,
):

    side = side.upper()
    title = f"📊 {escape(symbol)} INSTITUTIONAL SETUP"

    direction_emoji = "🟢" if side == "BUY" else "🔴"
    bias_text = _fmt_reason(higher_bias)
    bos_text = _fmt_reason(m15_bos)
    choch_text = _fmt_reason(choch)
    liquidity_text = _fmt_reason(liquidity)
    ob_text = _fmt_reason(order_block)
    fvg_text = _fmt_reason(fvg)

    lines = [
        f"<b>{title}</b>",
        "",
        f"🧭 H1 Bias → {bias_text}",
        f"🏗️ M15 Structure → {bos_text}{f' | {choch_text}' if choch else ''}",
        f"💧 Liquidity → {liquidity_text}",
        f"🏦 Order Block → {ob_text}",
        f"📦 FVG → {fvg_text}",
        "",
    ]

    if market_narrative:
        lines.append(f"🧠 Market Narrative → {escape(str(market_narrative))}")

    if setup_reason:
        lines.append(f"📌 Setup Reason → {escape(str(setup_reason))}")

    if trigger_note:
        lines.append(f"⚡ M1 Trigger → {escape(str(trigger_note))}")

    if entry_low is not None or entry_high is not None:
        lines.append(f"🎯 ENTRY → {_fmt_price(entry_low)} - {_fmt_price(entry_high)}")

    if stop_loss is not None:
        lines.append(f"🛑 SL → {_fmt_price(stop_loss)}")

    if targets:
        lines.append(_format_target_rows(targets))

    lines.extend([
        "",
        f"📊 Confidence → {_fmt_pct(confidence)}",
        f"🎓 Setup Grade → {_setup_grade(confidence)}",
    ])

    if session:
        lines.append(f"🕒 Session → {escape(str(session))}")

    if wait_note:
        lines.append(f"⚠️ {escape(str(wait_note))}")

    if trade_plan:
        lines.append("")
        lines.append(f"{direction_emoji} Plan Focus → {escape(str(trade_plan))}")

    return _format_lines(lines)


def build_premium_watch_message(
    symbol,
    side,
    watch_level=None,
    invalidation=None,
    trigger=None,
    score=None,
    reasons=None,
):

    side = side.upper()
    direction = "breakout" if side == "BUY" else "breakdown"

    lines = [
        f"⏳ <b>{escape(symbol)} M1 PRE-ENTRY WATCH</b>",
        "",
        f"Direction → {escape(side)}",
        f"Watch Level → {_fmt_price(watch_level)}",
        f"Invalidation → {_fmt_price(invalidation)}",
        f"Trigger → {_fmt_reason(trigger)}",
        f"Score → {_fmt_reason(score)}",
        "",
        f"Wait for the M1 {direction} confirmation before entry.",
    ]

    if reasons:
        lines.append("")
        lines.append("Why it matters:")
        for reason in reasons[:5]:
            lines.append(f"• {escape(str(reason))}")

    return _format_lines(lines)