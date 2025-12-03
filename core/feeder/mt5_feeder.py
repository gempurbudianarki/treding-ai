from typing import Optional

import MetaTrader5 as mt5
import pandas as pd
from loguru import logger

from config.settings import settings


TIMEFRAME_MAP = {
    1: mt5.TIMEFRAME_M1,
    5: mt5.TIMEFRAME_M5,
    15: mt5.TIMEFRAME_M15,
    30: mt5.TIMEFRAME_M30,
    60: mt5.TIMEFRAME_H1,
}


class MT5Feeder:
    def __init__(self) -> None:
        self.symbol: str = settings.SYMBOL
        self.tf_minutes: int = settings.TIMEFRAME_MINUTES
        self.timeframe = TIMEFRAME_MAP.get(self.tf_minutes, mt5.TIMEFRAME_M15)

    def initialize(self) -> bool:
        """
        Inisialisasi koneksi ke MT5.

        - Kalau MT5_PATH di .env ada dan valid -> pakai itu.
        - Kalau MT5_PATH tidak di-set / kosong -> pakai mt5.initialize() default.
        """
        logger.info("Inisialisasi MT5...")

        try:
            if settings.MT5_PATH:
                logger.info('Mencoba initialize MT5 dengan path: {}', settings.MT5_PATH)
                ok = mt5.initialize(path=settings.MT5_PATH)
            else:
                logger.info("MT5_PATH tidak di-set. Mencoba initialize MT5 tanpa path (default).")
                ok = mt5.initialize()

            if not ok:
                logger.error("Gagal initialize MT5: {}", mt5.last_error())
                return False
        except Exception as e:
            logger.error("Exception saat initialize MT5: {}", e)
            return False

        # login kalau credential lengkap, kalau tidak ya pakai session yang sudah login di terminal
        if settings.MT5_LOGIN and settings.MT5_PASSWORD and settings.MT5_SERVER:
            logger.info(
                "Mencoba login ke MT5: login={}, server={}",
                settings.MT5_LOGIN,
                settings.MT5_SERVER,
            )
            authorized = mt5.login(
                login=settings.MT5_LOGIN,
                password=settings.MT5_PASSWORD,
                server=settings.MT5_SERVER,
            )
            if not authorized:
                logger.error("Gagal login MT5: {}", mt5.last_error())
                return False
            logger.info("Berhasil login ke MT5.")
        else:
            logger.warning(
                "MT5_LOGIN / PASSWORD / SERVER tidak lengkap. "
                "Diasumsikan sudah login via terminal MT5."
            )

        # pastikan symbol tersedia
        if not mt5.symbol_select(self.symbol, True):
            logger.error("Gagal select symbol {}: {}", self.symbol, mt5.last_error())
            return False

        logger.info("MT5Feeder siap. Symbol: {}, TF: {}m", self.symbol, self.tf_minutes)
        return True

    def get_history(self, bars: int = 500) -> Optional[pd.DataFrame]:
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, bars)
        if rates is None:
            logger.error("Gagal ambil data rates: {}", mt5.last_error())
            return None

        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df.set_index("time", inplace=True)
        return df

    def get_tick_info(self) -> Optional[dict]:
        tick = mt5.symbol_info_tick(self.symbol)
        if not tick:
            logger.error("Gagal ambil tick info: {}", mt5.last_error())
            return None
        return {
            "bid": tick.bid,
            "ask": tick.ask,
            "last": tick.last,
            "time": tick.time,
        }
