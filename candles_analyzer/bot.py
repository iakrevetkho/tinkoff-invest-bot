import random

from enum import Enum

class RsiSignal(Enum):
    NaN = 1
    OverBought = 2
    OverSold = 3

class MacdSignal(Enum):
    NaN = 1
    GoUp = 2
    GoDown = 3

class TradingBot:
    def __init__(self, stop_loss=0.05):
        # RSI thresholds
        self.rsi_oversold_threshold = 30
        self.rsi_overbought_threshold = 70

        # Stop loss
        self.stop_loss = stop_loss
        
        self.reset()
    
    def reset(self):
        # init flags
        # RSI
        self.rsi_signal = RsiSignal.NaN
        # MACD
        self.macd_prev_value = None
        self.macd_prev_diff = None
        self.macd_signal = MacdSignal.NaN
        
        # Bought price
        self.balance = 0
        # Profit
        self.profit = 0
        
        self.current_step = 0
    
    def _set_rsi_signal(self, rsi_value):
        # RSI flag conditions
        if rsi_value > self.rsi_overbought_threshold:
            self.rsi_signal = RsiSignal.OverBought
        elif rsi_value < self.rsi_oversold_threshold:
            self.rsi_signal = RsiSignal.OverSold

    def _set_macd_signal(self, macd_value):
        # Check that we have prev value for diff
        if self.macd_prev_value is not None:
            # Calc MACD diff
            macd_diff = macd_value - self.macd_prev_value

            # Check that we have prev diff for condition
            if self.macd_prev_diff is not None:
                # MACD flag conditions
                # GoUp - \_/
                # GoDown - /─\
                if (self.macd_prev_diff <= 0) & (macd_diff > 0):
                    # GoUp
                    self.macd_signal = MacdSignal.GoUp
                elif (self.macd_prev_diff >= 0) & (macd_diff < 0):
                    # GoDown
                    self.macd_signal = MacdSignal.GoDown

            # Save current diff value as previous
            self.macd_prev_diff = macd_diff

        # Save current value as previous
        self.macd_prev_value = macd_value


    def _buy(self, current_price):
        print("Step: %d Buy with price=%f" % (self.current_step, current_price))

        # Set balance
        self.balance = current_price
        
    
    def _sell(self, current_price):
        # Calc profit
        profit = (current_price - self.balance) / self.balance

        # Check that we can sell
        if self.balance != 0:
            self.profit += profit
            
            print("Step: %d Sell with price=%f and profit %.2f%%" % (self.current_step, current_price, profit * 100))
            print("Overall Profit %.2f%%" % (self.profit * 100))
            
            # Set balance
            self.balance = 0
        else:
            print("ERROR. Can't sell, if we already sold.")
        

    def _check_stop_loss(self, current_price):
        # Calc profit
        profit = (current_price - self.balance) / self.balance

        if profit <= -self.stop_loss:
            print("Step: %d Stop loss from %.2f to %.2f with profit %.2f%%" % (self.current_step, self.balance, current_price, profit * 100))

            # Sell
            self._sell(current_price)


    def process(self, data):
        self.current_step += 1
        current_price = random.uniform(data["open_price"],data["close_price"])
        
        # Set RSI signal
        self._set_rsi_signal(data["RSI"])

        # Set MACD signal
        self._set_macd_signal(data["MACD"])

        if self.balance == 0:
            # Try to find buy signal
            if (self.rsi_signal == RsiSignal.OverSold) & (self.macd_signal == MacdSignal.GoUp):
                # Buy
                self._buy(current_price)

        else:
            # Try to find sell signal
            if (self.rsi_signal == RsiSignal.OverBought) & (self.macd_signal == MacdSignal.GoDown):
                # Sell
                self._sell(current_price)
            else:
                # Check stop-loss
                self._check_stop_loss(current_price)
                