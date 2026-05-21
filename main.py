import time

from config.settings import *

from mt5.connect import connect_mt5
from mt5.market_data import get_data

from indicators.rsi import add_rsi
from indicators.ema import add_ema

from strategy.engulfing_strategy import check_engulfing

from telegram_bot.bot import send_telegram
# --------------------------
# CONNECT MT5
# --------------------------
if not connect_mt5():
    quit()

send_telegram("🚀 XAUUSD AI BOT STARTED")

# --------------------------
# MAIN LOOP
# --------------------------
while True:

    try:

        # Get Data
        df = get_data(SYMBOL, ENTRY_TIMEFRAME)

        # Indicators
        df = add_rsi(df)
        df = add_ema(df)

        # Strategy
        signal, confidence = check_engulfing(df)

        # Last Price
        last_price = df.iloc[-1]['close']

        if signal:

            if signal == "BUY":

                tp1 = last_price + 3
                tp2 = last_price + 6
                tp3 = last_price + 9
                tp4 = last_price + 12
                tp5 = last_price + 15

                sl = last_price - 10

            else:

                tp1 = last_price - 3
                tp2 = last_price - 6
                tp3 = last_price - 9
                tp4 = last_price - 12
                tp5 = last_price - 15

                sl = last_price + 10

            message = f'''
🚨 XAUUSD {signal} SIGNAL 🚨

{"🟢" if signal=="BUY" else "🔴"} GOLD {signal} @ {last_price:.2f}

🎯 TP1 → {tp1:.2f}
🎯 TP2 → {tp2:.2f}
🎯 TP3 → {tp3:.2f}
🎯 TP4 → {tp4:.2f}
🎯 TP5 → {tp5:.2f}

🛑 SL → {sl:.2f}

📊 Confidence → {confidence}%

⚡ Strategy → Scalping + Intraday
📉 Trend Confirmation Active
'''

            print(message)

            send_telegram(message)

    except Exception as e:

        print("ERROR:", e)

    time.sleep(60)