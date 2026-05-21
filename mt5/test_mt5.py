import MetaTrader5 as mt5

print("Starting MT5 test...")

# Initialize MT5
mt5.initialize(
    path=r"C:\Program Files\MetaTrader 5\terminal64.exe"
)

print("MT5 connected successfully!")

# Account info
account_info = mt5.account_info()

if account_info is None:
    print("Failed to get account info")
else:
    print("Login:", account_info.login)
    print("Server:", account_info.server)
    print("Balance:", account_info.balance)

# Shutdown
mt5.shutdown()

print("Test completed")