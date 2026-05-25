import time
import traceback

from config.settings import *
from strategy.higher_timeframe import get_higher_timeframe_bias

from mt5.connect import connect_mt5
from mt5.market_data import get_data

from indicators.rsi import add_rsi
from indicators.ema import add_ema
from indicators.atr import add_atr
from strategy.order_blocks import detect_order_block
from strategy.fvg import detect_fvg

from strategy.breakout_analysis import analyze_breakout
from strategy.session_filter import allowed_session
from strategy.retest_strategy import retest_confirmation
from strategy.m1_entry import get_m1_sniper_entry
from strategy.dynamic_targets import build_dynamic_trade_plan
from strategy.market_regime import classify_market_regime, direction_allowed
from strategy.premium_signal_formatter import (
    build_premium_setup_message,
    build_premium_watch_message,
)
from strategy.market_structure import detect_market_structure
from strategy.liquidity_sweep import detect_liquidity_sweep

from telegram_bot.bot import send_telegram
from strategy.ai_confidence import calculate_confidence
from telegram_bot.live_commentary import (
    build_commentary_payload,
    build_market_update,
    build_market_update_html,
    state_has_meaningful_change,
)

# --------------------------------
# CONNECT MT5
# --------------------------------
if not connect_mt5():
    quit()

print("🚀 BOT STARTED")

send_telegram("🚀 XAUUSD AI BOT STARTED")

# --------------------------------
# TRADE STATE
# --------------------------------
active_trade = None
plan_sent = False
m1_watch_sent = False
last_regime = None

# --------------------------------
# LIVE COMMENTARY SETTINGS
# --------------------------------
COMMENTARY_INTERVAL_SECONDS = 300
last_commentary_time = 0
last_commentary_state = None

# --------------------------------
# MAIN LOOP
# --------------------------------
while True:

    try:

        # --------------------------------
        # SESSION FILTER
        # --------------------------------
        if not allowed_session():

            print("Outside trading session")

            time.sleep(60)

            continue

        # --------------------------------
        # GET MARKET DATA
        # --------------------------------
        # --------------------------------
        # LOAD MULTIPLE TIMEFRAMES
        # --------------------------------

        h1_df = get_data(SYMBOL, H1_TIMEFRAME)

        m15_df = get_data(SYMBOL, M15_TIMEFRAME)

        m5_df = get_data(SYMBOL, M5_TIMEFRAME)

        m1_df = get_data(SYMBOL, M1_TIMEFRAME)

        # Main execution dataframe
        df = m5_df
        h1_df = add_ema(h1_df)
        m15_df = add_ema(m15_df)

        higher_bias = get_higher_timeframe_bias(h1_df)

        m1_df = add_rsi(m1_df)
        m1_df = add_ema(m1_df)
        m1_df = add_atr(m1_df)

        # --------------------------------
        # ADD INDICATORS
        # --------------------------------
        df = add_rsi(df)
        df = add_ema(df)
        df = add_atr(df)

        # --------------------------------
        # CURRENT MARKET DATA
        # --------------------------------
        last_price = df.iloc[-1]['close']
        current_high = df.iloc[-1]['high']
        current_low = df.iloc[-1]['low']

        # --------------------------------
        # BREAKOUT ANALYSIS
        # --------------------------------
        analysis = analyze_breakout(df)

        support = analysis['support']
        resistance = analysis['resistance']
        trend = analysis['trend']

        # --------------------------------
        # MARKET STRUCTURE
        # --------------------------------
        structure = detect_market_structure(m15_df)

        bos = structure['bos']
        choch = structure['choch']

        # --------------------------------
        # LIQUIDITY SWEEP
        # --------------------------------
        liquidity = detect_liquidity_sweep(df)
        order_blocks = detect_order_block(df)

        bullish_ob = order_blocks['bullish_ob']
        bearish_ob = order_blocks['bearish_ob']

        sweep = liquidity['sweep']
        fvg = detect_fvg(df)

        bullish_fvg = fvg['bullish_fvg']
        bearish_fvg = fvg['bearish_fvg']

        market_regime = classify_market_regime(
            higher_bias=higher_bias,
            m15_trend=trend,
            bos=bos,
            choch=choch,
            sweep=sweep,
            support=support,
            resistance=resistance,
            price=last_price,
        )

        # --------------------------------
        # BUILD CURRENT STATE FOR LIVE COMMENTARY
        # --------------------------------
        reaction_zone = None
        if bullish_ob is not None:
            reaction_zone = f"Bullish OB at {bullish_ob:.2f}"
        elif bearish_ob is not None:
            reaction_zone = f"Bearish OB at {bearish_ob:.2f}"

        current_state = {
            "symbol": SYMBOL,
            "timeframe_bias": higher_bias,
            "market_regime": market_regime["regime"],
            "price": last_price,
            "reaction_zone": reaction_zone,
            "liquidity": sweep,
            "invalidation": f"Close above {resistance:.2f}" if higher_bias == 'BEARISH' else f"Close below {support:.2f}",
            "confirmations": [
                "M1 closed-candle confirmation",
            ],
            "waiting_for": [
                "Price reaction at OB/FVG",
                "Liquidity sweep or structure break",
            ],
            "expectations": [
                f"If {support:.2f} breaks and M1 confirms, sell-side exposure increases" if higher_bias == 'BEARISH' else f"If {resistance:.2f} breaks and M1 confirms, buy-side exposure increases",
            ],
            "session": "Active" if allowed_session() else "Closed",
            "notes": None,
            "entry_status": "No entry — monitoring",
            "bos": bos,
            "choch": choch,
            "support": support,
            "resistance": resistance,
            "sweep": sweep,
            "bullish_ob": bullish_ob,
            "bearish_ob": bearish_ob,
            "bullish_fvg": bullish_fvg,
            "bearish_fvg": bearish_fvg,
            # small recent series for sparkline
            "price_series": list(df['close'].iloc[-20:].astype(float)) if len(df) >= 20 else list(df['close'].astype(float)),
        }

        # decide if we should send commentary
        changed, reasons = state_has_meaningful_change(last_commentary_state, current_state)
        commentary_payload = build_commentary_payload(current_state, last_commentary_state)
        now = time.time()
        elapsed = (now - last_commentary_time) >= COMMENTARY_INTERVAL_SECONDS
        high_priority_event = bool(commentary_payload.get("events"))
        send_due = (high_priority_event or elapsed) and changed

        if send_due:
            html_message = build_market_update_html(commentary_payload)
            print("Sending live commentary (reasons):", reasons, "events:", commentary_payload.get("events", []))
            send_telegram(html_message, parse_mode="HTML")
            last_commentary_time = now
            last_commentary_state = current_state

        # --------------------------------
        # SEND MARKET PLAN
        # --------------------------------
        if not plan_sent:

            analysis_message = f"""
📊 XAUUSD SMART MONEY PLAN

💰 Current Price → {last_price:.2f}

        🧭 H1 Trend → {higher_bias}
        🏗️ M15 BOS → {bos}
        🔄 M15 CHOCH → {choch}
        ⚙️ M5 Trend → {trend}
        🎯 M5 Breakout Side → {analysis['breakout_side']}

🔴 Resistance → {resistance:.2f}
🟢 Support → {support:.2f}

💧 Liquidity Sweep → {sweep}
🏦 Bullish OB → {bullish_ob}
🏦 Bearish OB → {bearish_ob}
📦 Bullish FVG → {bullish_fvg}
📦 Bearish FVG → {bearish_fvg}

⚠️ Waiting for institutional setup
"""

            print(analysis_message)

            send_telegram(analysis_message)

            plan_sent = True

        # --------------------------------
        # RETEST CONFIRMATION
        # --------------------------------
        signal = retest_confirmation(
            df,
            resistance,
            support
        )

        print("Retest Signal:", signal)

        if last_regime != market_regime["regime"]:
            print("Market regime:", market_regime["regime"], "|", market_regime["summary"])
            last_regime = market_regime["regime"]

        if signal is None:

            m1_watch_sent = False

        # --------------------------------
        # NEW TRADE
        # --------------------------------
        if active_trade is None and signal:

            # --------------------------------
            # SMART MONEY FILTERS
            # --------------------------------
            # --------------------------------
            # INSTITUTIONAL FILTERS
            # --------------------------------

            if market_regime["regime"].startswith("TRENDING_BEARISH") and signal == "BUY":
                print("BUY blocked: bearish trending regime -> treat bullish reactions as pullbacks only")
                signal = None

            elif market_regime["regime"].startswith("TRENDING_BULLISH") and signal == "SELL":
                print("SELL blocked: bullish trending regime -> treat bearish reactions as pullbacks only")
                signal = None

            elif market_regime["regime"] == "RANGE":
                # In range conditions we only want fades from the extremes, not breakout chasing.
                if signal == "BUY" and not (last_price <= support or sweep == "BUY"):
                    print("BUY blocked: range regime requires support-side rejection or buy-side sweep")
                    signal = None
                elif signal == "SELL" and not (last_price >= resistance or sweep == "SELL"):
                    print("SELL blocked: range regime requires resistance-side rejection or sell-side sweep")
                    signal = None

            # BUY FILTER
            if signal == "BUY":
                allowed, regime_name = direction_allowed(market_regime, "BUY")
                if not allowed:
                    print(f"BUY blocked by regime filter: {regime_name}")
                    signal = None

            if signal == "BUY":
                if (
                    higher_bias != "BULLISH"
                    or bos != "BULLISH"
                    or trend != "BULLISH"
                    or analysis["breakout_side"] not in (None, "BUY")
                    or bullish_ob is None
                    or bullish_fvg is None
                ):

                    signal = None

                # SELL FILTER
            elif signal == "SELL":
                allowed, regime_name = direction_allowed(market_regime, "SELL")
                if not allowed:
                    print(f"SELL blocked by regime filter: {regime_name}")
                    signal = None

            if signal == "SELL":
                if (
                    higher_bias != "BEARISH"
                    or bos != "BEARISH"
                    or trend != "BEARISH"
                    or analysis["breakout_side"] not in (None, "SELL")
                    or bearish_ob is None
                    or bearish_fvg is None
                 
                ):

                    signal = None
            # --------------------------------
            # VALID SMART MONEY SETUP
            # --------------------------------
            if signal:

                atr = df.iloc[-1]['atr']
                confidence = calculate_confidence(
                    signal,
                    bos,
                    sweep,
                    bullish_ob,
                    bearish_ob, 
                    bullish_fvg,
                    bearish_fvg,
                    trend
                )
                # Reject weak setups
                if confidence < 70:
                    print("Weak setup rejected")

                    signal = None

                m1_trigger = None

                if signal:

                    m1_trigger = get_m1_sniper_entry(
                        m1_df,
                        signal,
                        support=support,
                        resistance=resistance,
                        higher_bias=higher_bias
                    )

                    if not m1_trigger["confirmed"]:

                        print(
                            "M1 trigger not confirmed:",
                            m1_trigger["trigger"],
                            m1_trigger["reasons"]
                        )

                        if not m1_watch_sent:

                            watch_message = build_premium_watch_message(
                                SYMBOL,
                                signal,
                                watch_level=resistance if signal == "BUY" else support,
                                invalidation=support if signal == "BUY" else resistance,
                                trigger=m1_trigger["trigger"],
                                score=m1_trigger["score"],
                                reasons=m1_trigger["reasons"]
                            )

                            print(watch_message)

                            send_telegram(watch_message, parse_mode="HTML")

                            m1_watch_sent = True

                        signal = None

                # --------------------------------
                # BUY TRADE
                # --------------------------------
                if signal == "BUY":

                    entry = m1_trigger["entry_price"] or last_price
                    trade_plan = build_dynamic_trade_plan(
                        "BUY",
                        entry,
                        m5_df,
                        m15_df=m15_df,
                        support=support,
                        resistance=resistance,
                        bullish_fvg=bullish_fvg,
                        bearish_fvg=bearish_fvg,
                        atr=m1_trigger["atr"] or df.iloc[-1]['atr'],
                        higher_bias=higher_bias,
                        trend=trend
                    )

                    tp1 = trade_plan["targets"][0]["price"]
                    tp2 = trade_plan["targets"][1]["price"]
                    tp3 = trade_plan["targets"][2]["price"]
                    sl = trade_plan["stop_loss"]
                    entry_low = min(entry, entry + (trade_plan["risk"] * 0.15)) if signal == "BUY" else min(entry - (trade_plan["risk"] * 0.15), entry)
                    entry_high = max(entry, entry + (trade_plan["risk"] * 0.15)) if signal == "BUY" else max(entry - (trade_plan["risk"] * 0.15), entry)

                    signal_message = build_premium_setup_message(
                        SYMBOL,
                        "BUY",
                        higher_bias=higher_bias,
                        m15_bos=bos,
                        choch=choch,
                        liquidity=f"{sweep or 'No sweep'}",
                        order_block=f"Valid bullish OB" if bullish_ob is not None else "No bullish OB",
                        fvg=f"Bullish imbalance active" if bullish_fvg is not None else "No bullish FVG",
                        entry_low=entry_low,
                        entry_high=entry_high,
                        stop_loss=sl,
                        targets=trade_plan["targets"],
                        confidence=confidence,
                        session="Confirmed",
                        wait_note="M1 bullish confirmation secured",
                        market_narrative="Aligned on multi-timeframe bullish structure",
                        setup_reason="M5 setup + M1 sniper confirmation",
                        trigger_note=m1_trigger["trigger"],
                        trade_plan=f"{trade_plan['targets'][0]['label']} / {trade_plan['targets'][1]['label']} / {trade_plan['targets'][2]['label']}"
                    )

                    active_trade = {
                        "side": "BUY",
                        "entry": entry,
                        "tp1": tp1,
                        "tp2": tp2,
                        "tp3": tp3,
                        "sl": sl,
                        "initial_sl": sl,
                        "trade_plan": trade_plan,
                        "tp1_hit": False,
                        "tp2_hit": False,
                        "tp3_hit": False
                    }

                    message = signal_message

                    print(message)

                    send_telegram(message, parse_mode="HTML")

                    m1_watch_sent = False

                # --------------------------------
                # SELL TRADE
                # --------------------------------
                elif signal == "SELL":

                    entry = m1_trigger["entry_price"] or last_price
                    trade_plan = build_dynamic_trade_plan(
                        "SELL",
                        entry,
                        m5_df,
                        m15_df=m15_df,
                        support=support,
                        resistance=resistance,
                        bullish_fvg=bullish_fvg,
                        bearish_fvg=bearish_fvg,
                        atr=m1_trigger["atr"] or df.iloc[-1]['atr'],
                        higher_bias=higher_bias,
                        trend=trend
                    )

                    tp1 = trade_plan["targets"][0]["price"]
                    tp2 = trade_plan["targets"][1]["price"]
                    tp3 = trade_plan["targets"][2]["price"]
                    sl = trade_plan["stop_loss"]
                    entry_low = min(entry - (trade_plan["risk"] * 0.15), entry) if signal == "SELL" else min(entry, entry + (trade_plan["risk"] * 0.15))
                    entry_high = max(entry - (trade_plan["risk"] * 0.15), entry) if signal == "SELL" else max(entry, entry + (trade_plan["risk"] * 0.15))

                    signal_message = build_premium_setup_message(
                        SYMBOL,
                        "SELL",
                        higher_bias=higher_bias,
                        m15_bos=bos,
                        choch=choch,
                        liquidity=f"{sweep or 'No sweep'}",
                        order_block=f"Valid bearish OB" if bearish_ob is not None else "No bearish OB",
                        fvg=f"Bearish imbalance active" if bearish_fvg is not None else "No bearish FVG",
                        entry_low=entry_low,
                        entry_high=entry_high,
                        stop_loss=sl,
                        targets=trade_plan["targets"],
                        confidence=confidence,
                        session="Confirmed",
                        wait_note="M1 bearish confirmation secured",
                        market_narrative="Aligned on multi-timeframe bearish structure",
                        setup_reason="M5 setup + M1 sniper confirmation",
                        trigger_note=m1_trigger["trigger"],
                        trade_plan=f"{trade_plan['targets'][0]['label']} / {trade_plan['targets'][1]['label']} / {trade_plan['targets'][2]['label']}"
                    )

                    active_trade = {
                        "side": "SELL",
                        "entry": entry,
                        "tp1": tp1,
                        "tp2": tp2,
                        "tp3": tp3,
                        "sl": sl,
                        "initial_sl": sl,
                        "trade_plan": trade_plan,
                        "tp1_hit": False,
                        "tp2_hit": False,
                        "tp3_hit": False
                    }

                    message = signal_message

                    print(message)

                    send_telegram(message, parse_mode="HTML")

                    m1_watch_sent = False

        # --------------------------------
        # ACTIVE TRADE MANAGEMENT
        # --------------------------------
        if active_trade:

            side = active_trade["side"]

            # --------------------------------
            # BUY TRADE
            # --------------------------------
            if side == "BUY":

                # TP1
                if (
                    current_high >= active_trade["tp1"]
                    and not active_trade["tp1_hit"]
                ):

                    active_trade["tp1_hit"] = True

                    if active_trade["side"] == "BUY" and active_trade["sl"] < active_trade["entry"]:

                        active_trade["sl"] = active_trade["entry"]

                    elif active_trade["side"] == "SELL" and active_trade["sl"] > active_trade["entry"]:

                        active_trade["sl"] = active_trade["entry"]

                    send_telegram("✅ BUY TP1 HIT - SL MOVED TO BREAKEVEN")

                # TP2
                if (
                    current_high >= active_trade["tp2"]
                    and not active_trade["tp2_hit"]
                ):

                    active_trade["tp2_hit"] = True

                    send_telegram("✅ BUY TP2 HIT")

                # TP3
                if (
                    current_high >= active_trade["tp3"]
                    and not active_trade["tp3_hit"]
                ):

                    active_trade["tp3_hit"] = True

                    send_telegram("🏆 BUY TP3 HIT — TRADE COMPLETED")

                    active_trade = None
                    plan_sent = False

                # STOP LOSS
                if current_low <= active_trade["sl"]:

                    send_telegram("❌ BUY STOP LOSS HIT")

                    active_trade = None
                    plan_sent = False

            # --------------------------------
            # SELL TRADE
            # --------------------------------
            elif side == "SELL":

                # TP1
                if (
                    current_low <= active_trade["tp1"]
                    and not active_trade["tp1_hit"]
                ):

                    active_trade["tp1_hit"] = True

                    if active_trade["side"] == "BUY" and active_trade["sl"] < active_trade["entry"]:

                        active_trade["sl"] = active_trade["entry"]

                    elif active_trade["side"] == "SELL" and active_trade["sl"] > active_trade["entry"]:

                        active_trade["sl"] = active_trade["entry"]

                    send_telegram("✅ SELL TP1 HIT - SL MOVED TO BREAKEVEN")

                # TP2
                if (
                    current_low <= active_trade["tp2"]
                    and not active_trade["tp2_hit"]
                ):

                    active_trade["tp2_hit"] = True

                    send_telegram("✅ SELL TP2 HIT")

                # TP3
                if (
                    current_low <= active_trade["tp3"]
                    and not active_trade["tp3_hit"]
                ):

                    active_trade["tp3_hit"] = True

                    send_telegram("🏆 SELL TP3 HIT — TRADE COMPLETED")

                    active_trade = None
                    plan_sent = False

                # STOP LOSS
                if current_high >= active_trade["sl"]:

                    send_telegram("❌ SELL STOP LOSS HIT")

                    active_trade = None
                    plan_sent = False

        # --------------------------------
        # DEBUG INFO
        # --------------------------------
        print("Current Price:", last_price)
        print("Trend:", trend)
        print("BOS:", bos)
        print("CHOCH:", choch)
        print("Liquidity Sweep:", sweep)

    except Exception as e:

        print("ERROR:", e)
        traceback.print_exc()

    # --------------------------------
    # LOOP DELAY
    # --------------------------------
    time.sleep(1)