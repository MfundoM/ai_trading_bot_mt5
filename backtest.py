import MetaTrader5 as mt5
import pandas as pd
import backtrader as bt
import time
import numpy as np

# --- Initialize MetaTrader5 ---
if not mt5.initialize():
    print("MetaTrader5 initialization failed")
    quit()

# --- Fetch Historical Data from MetaTrader5 ---
def get_historical_data(symbol, timeframe, bars):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
    data = pd.DataFrame(rates)
    data['time'] = pd.to_datetime(data['time'], unit='s')
    data.set_index('time', inplace=True)
    return data

# --- Backtrader Strategy ---
class MyStrategy(bt.Strategy):
    # Define the indicators we will use
    params = (
        ('rsi_period', 14),
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('bollinger_period', 20),
        ('bollinger_dev', 2),
        ('rsi_overbought', 70),
        ('rsi_oversold', 30),
        ('stop_loss', 10),  # Stop loss in pips
        ('take_profit', 20),  # Take profit in pips
        ('lot_size', 1.0),
    )

    def __init__(self):
        # Initialize the indicators
        self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
        self.macd = bt.indicators.MACD(
            self.data.close, period_me1=self.params.macd_fast,
            period_me2=self.params.macd_slow, period_signal=self.params.macd_signal)
        self.bbands = bt.indicators.BollingerBands(
            self.data.close, period=self.params.bollinger_period, devfactor=self.params.bollinger_dev)

    def next(self):
        # Access the latest price and indicators
        price = self.data.close[0]
        rsi_value = self.rsi[0]
        macd_value = self.macd.macd[0]
        macd_signal_value = self.macd.signal[0]
        upper_band = self.bbands.lines.bot[0]
        lower_band = self.bbands.lines.top[0]

        # Buy Signal Logic
        if rsi_value < self.params.rsi_oversold and macd_value > macd_signal_value and price <= lower_band:
            if not self.position:
                self.buy(size=self.params.lot_size)
                print(f"BUY at {price} - RSI: {rsi_value}, MACD: {macd_value}")

        # Sell Signal Logic
        elif rsi_value > self.params.rsi_overbought and macd_value < macd_signal_value and price >= upper_band:
            if not self.position:
                self.sell(size=self.params.lot_size)
                print(f"SELL at {price} - RSI: {rsi_value}, MACD: {macd_value}")

    def stop(self):
        # Print strategy performance stats
        print(f"Final Portfolio Value: {self.broker.getvalue()}")

# --- Backtest Setup ---
def run_backtest(symbol, timeframe, bars):
    # Fetch historical data
    data = get_historical_data(symbol, timeframe, bars)

    # Convert the DataFrame to Backtrader format
    data_feed = bt.feeds.PandasData(dataname=data)

    # Initialize Backtrader engine
    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)
    cerebro.addstrategy(MyStrategy)
    cerebro.broker.set_cash(10000)  # Initial capital
    cerebro.broker.set_commission(commission=0.001)  # Commission per trade (0.1%)

    # Run the strategy
    print(f"Starting Portfolio Value: {cerebro.broker.getvalue()}")
    cerebro.run()
    print(f"Ending Portfolio Value: {cerebro.broker.getvalue()}")

# --- Main Execution ---
if __name__ == "__main__":
    symbol = "VIX"  # The symbol to backtest
    timeframe = mt5.TIMEFRAME_M1  # 1-minute data
    bars = 1000  # Number of bars to fetch for the backtest

    run_backtest(symbol, timeframe, bars)
