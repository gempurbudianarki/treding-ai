import pandas as pd
import numpy as np
from loguru import logger

class TechnicalBrain:

    def __init__(self):
        logger.info("TechnicalBrain loaded with EMA, RSI, MACD, STOCH, ATR")

    def analyze(self, df: pd.DataFrame):
        """
        df = MT5 feeder already gives OHLC data
        """

        try:
            close = df['close']

            # EMA
            df['ema_fast'] = close.ewm(span=20).mean()
            df['ema_slow'] = close.ewm(span=50).mean()

            # RSI
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))

            # MACD
            ema12 = close.ewm(span=12).mean()
            ema26 = close.ewm(span=26).mean()
            df['macd'] = ema12 - ema26
            df['signal'] = df['macd'].ewm(span=9).mean()

            # Stochastic
            low14 = df['low'].rolling(14).min()
            high14 = df['high'].rolling(14).max()
            df['stoch'] = 100 * ((df['close'] - low14) / (high14 - low14))

            # ATR
            df['tr'] = np.maximum(df['high'] - df['low'],
                                  np.maximum(abs(df['high'] - df['close'].shift()),
                                             abs(df['low'] - df['close'].shift())))
            df['atr'] = df['tr'].rolling(14).mean()

            last = df.iloc[-1]

            # === SCORE CALCULATION ===
            buy_score = 0
            sell_score = 0

            # Trend → EMA crossover
            if last['ema_fast'] > last['ema_slow']:
                buy_score += 1
            else:
                sell_score += 1

            # RSI Logic
            if last['rsi'] < 35:
                buy_score += 1
            elif last['rsi'] > 65:
                sell_score += 1

            # MACD momentum
            if last['macd'] > last['signal']:
                buy_score += 1
            else:
                sell_score += 1

            # Stochastic timing
            if last['stoch'] < 25:
                buy_score += 1
            elif last['stoch'] > 75:
                sell_score += 1

            # ATR filter → if ATR too small = sideways
            if last['atr'] < df['atr'].mean() * 0.7:
                logger.debug("ATR low → sideways → signal weakened")
                buy_score *= 0.8
                sell_score *= 0.8

            # Decision
            diff = buy_score - sell_score
            conf = min(1.0, abs(diff) / 4)

            if diff > 0:
                direction = "buy"
            elif diff < 0:
                direction = "sell"
            else:
                direction = "neutral"

            logger.debug(
                f"TechnicalBrain => buy_score={buy_score}, sell_score={sell_score}, "
                f"dir={direction}, conf={conf}"
            )

            return {
                     "direction": direction,
                     "confidence": conf,
                     "buy_score": buy_score,
                     "sell_score": sell_score
}


        except Exception as e:
            logger.error(f"TechnicalBrain ERROR: {e}")
            return "neutral", 0.1
