import MetaTrader5 as mt5

if not mt5.initialize():
    print("MetaTrader5 initialization failed")
    quit()

account_info = mt5.account_info()
if account_info is not None:
    print(account_info)
else:
    print("Failed to get account info")

mt5.shutdown()

