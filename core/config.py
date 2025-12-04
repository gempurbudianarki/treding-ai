from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # === MT5 Config ===
    MT5_PATH: str = Field(default=r"C:\Program Files\MetaTrader 5\terminal64.exe")
    MT5_LOGIN: int = 5043244800
    MT5_PASSWORD: str = "@Gempur123"
    MT5_SERVER: str = "MetaQuotes-Demo"

    # === Trading Config ===
    SYMBOL: str = "XAUUSD"
    TIMEFRAME_MINUTES: int = 15
    DRY_RUN: bool = True

    # Mode trading: SAFE / BALANCED / AGGRESSIVE / SCALPING_M5
    TRADING_MODE: str = "SAFE"

    # Minimal confidence buat entry
    TECH_CONF_THRESHOLD: float = 0.20  

    # News sentiment ON/OFF
    USE_SENTIMENT: bool = True

    # API Keys
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # === Risk Management (dari config lama, tetap kita support) ===
    risk_per_trade_pct: float = 1.0
    max_daily_drawdown_pct: float = 3.0
    max_open_trades: int = 3
    loop_sleep_seconds: int = 60
    min_bars_required: int = 200

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # biar aman kalau ada variable tambahan


settings = Settings()
