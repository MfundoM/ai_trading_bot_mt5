import MetaTrader5 as mt5
import talib
import time

# --- Trading Settings ---
symbol = "VIX"  # Replace with your trading symbol (e.g., EURUSD, VIX, etc.)
lot_size = 1.0  # Lot size for orders (adjust to your risk)
rsi_period = 14  # RSI period for calculation
rsi_overbought = 70  # RSI value indicating overbought market
rsi_oversold = 30  # RSI value indicating oversold market
slippage = 10  # Maximum slippage in pips
stop_loss_distance = 10  # Distance for stop-loss in pips
take_profit_distance = 20  # Distance for take-profit in pips

# --- Initialize MetaTrader5 ---
if not mt5.initialize():
    print("MetaTrader5 initialization failed")
    quit()

# --- Function to Get Market Data ---
def get_latest_price(symbol):
    tick = mt5.symbol_info_tick(symbol)
    if tick:
        return tick.ask, tick.bid
    else:
        print(f"Failed to get market data for {symbol}")
        return None, None

# --- Function to Get RSI Value ---
def get_rsi(symbol, period):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, period)
    close_prices = [rate[4] for rate in rates]  # Close prices
    rsi = talib.RSI(close_prices, timeperiod=period)
    return rsi[-1]  # Latest RSI value

# --- Function to Place Buy Order ---
def place_buy_order(symbol, price):
    stop_loss = price - stop_loss_distance * 0.0001  # Stop loss in price
    take_profit = price + take_profit_distance * 0.0001  # Take profit in price

    # Prepare order request
    order = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "slippage": slippage,
        "stoploss": stop_loss,
        "takeprofit": take_profit,
        "deviation": 10,
        "magic": 123456,
        "comment": "RSI Bot Buy",
        "type_filling": mt5.ORDER_FILLING_IOC,
        "type_time": mt5.ORDER_TIME_GTC,
    }

    # Send the order
    result = mt5.order_send(order)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to place buy order. Error code: {result.retcode}")
    else:
        print("Buy order successfully placed!")

# --- Function to Place Sell Order ---
def place_sell_order(symbol, price):
    stop_loss = price + stop_loss_distance * 0.0001  # Stop loss in price
    take_profit = price - take_profit_distance * 0.0001  # Take profit in price

    # Prepare order request
    order = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_SELL,
        "price": price,
        "slippage": slippage,
        "stoploss": stop_loss,
        "takeprofit": take_profit,
        "deviation": 10,
        "magic": 123456,
        "comment": "RSI Bot Sell",
        "type_filling": mt5.ORDER_FILLING_IOC,
        "type_time": mt5.ORDER_TIME_GTC,
    }

    # Send the order
    result = mt5.order_send(order)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to place sell order. Error code: {result.retcode}")
    else:
        print("Sell order successfully placed!")

# --- Main Trading Logic ---
while True:
    print("\nChecking market conditions...")

    # Get the latest market price
    ask_price, bid_price = get_latest_price(symbol)
    if ask_price is None or bid_price is None:
        time.sleep(5)  # Wait for 5 seconds before retrying
        continue

    # Get the latest RSI value
    rsi_value = get_rsi(symbol, rsi_period)
    print(f"Current RSI: {rsi_value}")

    # If RSI is below 30 (oversold), place a buy order
    if rsi_value < rsi_oversold:
        print("RSI indicates oversold market. Placing buy order...")
        place_buy_order(symbol, ask_price)

    # If RSI is above 70 (overbought), place a sell order
    elif rsi_value > rsi_overbought:
        print("RSI indicates overbought market. Placing sell order...")
        place_sell_order(symbol, bid_price)

    # If RSI is in neutral range, do nothing
    else:
        print("RSI indicates neutral market. No action taken.")

    # Wait before checking again (e.g., check every minute)
    time.sleep(60)
