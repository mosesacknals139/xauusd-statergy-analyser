import time

from config.settings import *

from mt5.connect import connect_mt5
from mt5.market_data import get_data

from indicators.rsi import add_rsi
from indicators.ema import add_ema
from indicators.atr import add_atr

from strategy.breakout_analysis import analyze_breakout
from strategy.session_filter import allowed_session
from strategy.retest_strategy import retest_confirmation

from telegram_bot.bot import send_telegram

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
        # GET DATA
        # --------------------------------
        df = get_data(SYMBOL, ENTRY_TIMEFRAME)

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
        # SEND MARKET PLAN
        # --------------------------------
        if not plan_sent:

            analysis_message = f"""
📊 XAUUSD PROFESSIONAL TRADE PLAN

💰 Current Price → {last_price:.2f}

🔴 Resistance → {resistance:.2f}
🟢 Support → {support:.2f}

📈 Trend → {trend}

⚠️ Waiting for professional retest setup
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

        # --------------------------------
        # NEW TRADE
        # --------------------------------
        if active_trade is None and signal:

            atr = df.iloc[-1]['atr']

            # --------------------------------
            # BUY TRADE
            # --------------------------------
            if signal == "BUY":

                entry = last_price

                tp1 = entry + (atr * 1.5)
                tp2 = entry + (atr * 3)
                tp3 = entry + (atr * 5)

                sl = entry - (atr * 1.2)

                active_trade = {
                    "side": "BUY",
                    "entry": entry,
                    "tp1": tp1,
                    "tp2": tp2,
                    "tp3": tp3,
                    "sl": sl,
                    "tp1_hit": False,
                    "tp2_hit": False,
                    "tp3_hit": False
                }

                message = f"""
🚨 XAUUSD BUY RETEST ENTRY 🚨

🟢 BUY → {entry:.2f}

✅ Resistance Retest Confirmed
✅ Bullish Continuation
✅ Session Confirmed

🎯 TP1 → {tp1:.2f}
🎯 TP2 → {tp2:.2f}
🎯 TP3 → {tp3:.2f}

🛑 SL → {sl:.2f}

📈 Trend → {trend}

🔥 Professional Retest Entry
"""

                print(message)

                send_telegram(message)

            # --------------------------------
            # SELL TRADE
            # --------------------------------
            elif signal == "SELL":

                entry = last_price

                tp1 = entry - (atr * 1.5)
                tp2 = entry - (atr * 3)
                tp3 = entry - (atr * 5)

                sl = entry + (atr * 1.2)

                active_trade = {
                    "side": "SELL",
                    "entry": entry,
                    "tp1": tp1,
                    "tp2": tp2,
                    "tp3": tp3,
                    "sl": sl,
                    "tp1_hit": False,
                    "tp2_hit": False,
                    "tp3_hit": False
                }

                message = f"""
🚨 XAUUSD SELL RETEST ENTRY 🚨

🔴 SELL → {entry:.2f}

✅ Support Retest Confirmed
✅ Bearish Continuation
✅ Session Confirmed

🎯 TP1 → {tp1:.2f}
🎯 TP2 → {tp2:.2f}
🎯 TP3 → {tp3:.2f}

🛑 SL → {sl:.2f}

📉 Trend → {trend}

🔥 Professional Retest Entry
"""

                print(message)

                send_telegram(message)

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

                    send_telegram("✅ BUY TP1 HIT")

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

                # SL
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

                    send_telegram("✅ SELL TP1 HIT")

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

                # SL
                if current_high >= active_trade["sl"]:

                    send_telegram("❌ SELL STOP LOSS HIT")

                    active_trade = None
                    plan_sent = False

        # --------------------------------
        # DEBUG INFO
        # --------------------------------
        print("Current Price:", last_price)
        print("High:", current_high)
        print("Low:", current_low)

    except Exception as e:

        print("ERROR:", e)

    # --------------------------------
    # LOOP DELAY
    # --------------------------------
    time.sleep(1)