import MetaTrader5 as mt5

def connect_mt5():

    if not mt5.initialize():
        print("MT5 initialization failed")
        print(mt5.last_error())
        return False

    print("MT5 connected successfully")
    return True