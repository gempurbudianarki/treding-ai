import os
from dotenv import load_dotenv

# Load .env
load_dotenv()


class Settings:
    def __init__(self):
        # --- API Keys ---
        self.OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
        self.GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

        # --- MT5 ---
        self.MT5_PATH = os.getenv("MT5_PATH", r"C:\Program Files\MetaTrader 5\terminal64.exe")
        self.MT5_LOGIN = int(os.getenv("MT5_LOGIN", "0"))
        self.MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
        self.MT5_SERVER = os.getenv("MT5_SERVER", "MetaQuotes-Demo")

        # --- Trading Config ---
        self.SYMBOL = os.getenv("SYMBOL", "XAUUSD")
        self.TIMEFRAME = os.getenv("TIMEFRAME", "15m")
        self.DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

        # --- Sentiment ---
        self.SENTIMENT_MAX_AGE = int(os.getenv("SENTIMENT_MAX_AGE", "90"))

        # --- Logging ---
        self.LOG_PATH = "data/logs/bot.log"


settings = Settings()
