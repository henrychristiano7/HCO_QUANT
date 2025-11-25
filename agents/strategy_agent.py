# strategy_agent.py
# Uses AI to generate and backtest trading strategies
import backtrader as bt

class SimpleStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(period=20)

    def next(self):
        if self.data.close[0] > self.sma[0]:
            self.buy()
        elif self.data.close[0] < self.sma[0]:
            self.sell()

if __name__ == "__main__":
    print("⚙️ Running a sample backtest...")
