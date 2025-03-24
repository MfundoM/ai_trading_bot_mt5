import MetaTrader5 as mt5
import talib
import numpy as np

# --- Trading Settings ---
symbol = "VIX"  # Replace with your trading symbol (e.g., EURUSD, VIX, etc.)
lot_size = 1.0  # Lot size for orders
rsi_period = 14  # RSI period for calculation
macd_fastperiod = 12  # MACD fast period
macd_slowperiod = 26  # MACD slow period
macd_signalperiod = 9  # MACD signal period
bollinger_period = 20  # Bollinger Bands period
bollinger_deviation = 2  # Bollinger Bands deviation (standard deviation)
rsi_overbought = 70  # RSI value indicating overbought market
rsi_oversold = 30  # RSI value indicating oversold market
slippage = 10  # Slippage tolerance in pips
stop_loss_distance = 10  # Stop-loss distance in pips
take_profit_distance = 20  # Take-profit distance in pips

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

# --- Function to Get Indicators ---
def get_indicators(symbol, period):
    # Fetch historical data (1 minute timeframe)
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, period)
    close_prices = [rate[4] for rate in rates]  # Close prices

    # Calculate RSI
    rsi = talib.RSI(np.array(close_prices), timeperiod=rsi_period)
    
    # Calculate MACD
    macd, macd_signal, macd_hist = talib.MACD(np.array(close_prices),
                                              fastperiod=macd_fastperiod,
                                              slowperiod=macd_slowperiod,
                                              signalperiod=macd_signalperiod)
    
    # Calculate Bollinger Bands
    upper_band, middle_band, lower_band = talib.BBANDS(np.array(close_prices),
                                                        timeperiod=bollinger_period,
                                                        nbdevup=bollinger_deviation,
                                                        nbdevdn=bollinger_deviation,
                                                        matype=0)
    
    return rsi[-1], macd[-1], macd_signal[-1], upper_band[-1], middle_band[-1], lower_band[-1]

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
        "comment": "Strategy Buy",
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
        "comment": "Strategy Sell",
        "type_filling": mt5.ORDER_FILLING_IOC,
        "type_time": mt5.ORDER_TIME_GTC,
    }

    # Send the order
    result = mt5.order_send(order)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to place sell order. Error code: {result.retcode}")
    else:
        print("Sell order successfully placed!")

# --- Main Strategy Logic ---
def run_strategy():
    print("Running trading strategy...")

    # Get the latest market price
    ask_price, bid_price = get_latest_price(symbol)
    if ask_price is None or bid_price is None:
        return

    # Get technical indicators
    rsi_value, macd_value, macd_signal_value, upper_band, middle_band, lower_band = get_indicators(symbol, 50)
    print(f"RSI: {rsi_value}, MACD: {macd_value}, MACD Signal: {macd_signal_value}")
    print(f"Bollinger Bands: Upper={upper_band}, Middle={middle_band}, Lower={lower_band}")

    # Buy signal logic:
    # - RSI below 30 (oversold)
    # - MACD crossing above MACD Signal (bullish crossover)
    # - Price touches or bounces off the lower Bollinger Band
    if rsi_value < rsi_oversold and macd_value > macd_signal_value and bid_price <= lower_band:
        print("Buy signal detected!")
        place_buy_order(symbol, ask_price)

    # Sell signal logic:
    # - RSI above 70 (overbought)
    # - MACD crossing below MACD Signal (bearish crossover)
    # - Price touches or exceeds the upper Bollinger Band
    elif rsi_value > rsi_overbought and macd_value < macd_signal_value and ask_price >= upper_band:
        print("Sell signal detected!")
        place_sell_order(symbol, bid_price)

# --- Run the Strategy in a Loop ---
if __name__ == "__main__":
    while True:
        run_strategy()
        time.sleep(60)  # Run the strategy every minute (or adjust as needed)
