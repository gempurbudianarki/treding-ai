from typing import Optional

import MetaTrader5 as mt5
from loguru import logger

from config.settings import settings


class MT5Executor:
    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        self.dry_run = settings.DRY_RUN

    def _send_order(
        self,
        order_type: int,
        lot: float,
        price: Optional[float] = None,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
        comment: str = "",
    ) -> bool:
        symbol_info = mt5.symbol_info(self.symbol)
        if not symbol_info:
            logger.error("MT5Executor: gagal ambil symbol_info.")
            return False

        if price is None:
            tick = mt5.symbol_info_tick(self.symbol)
            if not tick:
                logger.error("MT5Executor: gagal ambil tick.")
                return False
            price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lot,
            "type": order_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 50,
            "magic": 123456,
            "comment": comment,
            "type_filling": mt5.ORDER_FILLING_FOK,
            "type_time": mt5.ORDER_TIME_GTC,
        }

        logger.info("MT5Executor request: {}", request)

        if self.dry_run:
            logger.info("[DRY_RUN] Tidak mengirim order ke MT5.")
            return True

        result = mt5.order_send(request)
        if result is None:
            logger.error("MT5Executor: order_send hasil None: {}", mt5.last_error())
            return False

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error("MT5Executor: order gagal, retcode={}, comment={}", result.retcode, result.comment)
            return False

        logger.info("Order berhasil: {}", result)
        return True

    def buy_market(self, lot: float, sl: Optional[float], tp: Optional[float], reason: str) -> bool:
        logger.info("Eksekusi BUY: lot={}, sl={}, tp={}, reason={}", lot, sl, tp, reason)
        return self._send_order(mt5.ORDER_TYPE_BUY, lot, sl=sl, tp=tp, comment=reason)

    def sell_market(self, lot: float, sl: Optional[float], tp: Optional[float], reason: str) -> bool:
        logger.info("Eksekusi SELL: lot={}, sl={}, tp={}, reason={}", lot, sl, tp, reason)
        return self._send_order(mt5.ORDER_TYPE_SELL, lot, sl=sl, tp=tp, comment=reason)
