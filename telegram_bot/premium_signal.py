def create_signal_message(
    signal,
    entry,
    sl,
    tp1,
    tp2,
    tp3,
    confidence,
    trend,
    higher_bias,
    bos,
    choch,
    sweep,
    bullish_ob,
    bearish_ob,
    bullish_fvg,
    bearish_fvg
):

    # --------------------------------
    # MARKET STORY
    # --------------------------------
    market_story = []

    if bos:
        market_story.append(f"🏗️ BOS → {bos}")

    if choch:
        market_story.append(f"🔄 CHOCH → {choch}")

    if sweep:
        market_story.append(f"💧 Liquidity Sweep → {sweep}")

    if bullish_ob or bearish_ob:
        market_story.append("🏦 Institutional Order Block Active")

    if bullish_fvg or bearish_fvg:
        market_story.append("📦 Fair Value Gap Active")

    market_text = "\n".join(market_story)

    # --------------------------------
    # SIGNAL TYPE
    # --------------------------------
    emoji = "🟢" if signal == "BUY" else "🔴"

    # --------------------------------
    # FINAL MESSAGE
    # --------------------------------
    message = f"""
━━━━━━━━━━━━━━━━━━
🚨 XAUUSD INSTITUTIONAL SIGNAL
━━━━━━━━━━━━━━━━━━

{emoji} SIGNAL → {signal}

🧭 H1 Bias → {higher_bias}
📈 Market Trend → {trend}

{market_text}

━━━━━━━━━━━━━━━━━━

🎯 ENTRY ZONE
→ {entry:.2f}

🛑 STOP LOSS
→ {sl:.2f}

🎯 TAKE PROFITS

TP1 → {tp1:.2f}
TP2 → {tp2:.2f}
TP3 → {tp3:.2f}

━━━━━━━━━━━━━━━━━━

📊 AI CONFIDENCE
→ {confidence}%

⚠️ Wait for candle confirmation before manual entry

🔥 Institutional Smart Money Setup
━━━━━━━━━━━━━━━━━━
"""

    return message
