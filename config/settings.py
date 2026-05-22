

import MetaTrader5 as mt5

# --------------------------------
# TELEGRAM
# --------------------------------
BOT_TOKEN = "8643017281:AAHW2K7_KunmghoIzv18BYvW0Aov0BZ3mjw"
CHAT_ID = "8549950808"

# --------------------------------
# SYMBOL
# --------------------------------
SYMBOL = "XAUUSD"

# --------------------------------
# MULTI TIMEFRAME SYSTEM
# --------------------------------

# H1 → Macro Trend
H1_TIMEFRAME = mt5.TIMEFRAME_H1

# M15 → Structure / BOS / CHOCH
M15_TIMEFRAME = mt5.TIMEFRAME_M15

# M5 → Main Setup
M5_TIMEFRAME = mt5.TIMEFRAME_M5

# M1 → Sniper Entry
M1_TIMEFRAME = mt5.TIMEFRAME_M1

# --------------------------------
# DEFAULT ENTRY TF
# --------------------------------
ENTRY_TIMEFRAME = M5_TIMEFRAME

# --------------------------------
# RISK SETTINGS
# --------------------------------
RISK_PER_TRADE = 1

# --------------------------------
# AI CONFIDENCE
# --------------------------------
CONFIDENCE_THRESHOLD = 70

# --------------------------------
# DATA
# --------------------------------
CANDLES = 500