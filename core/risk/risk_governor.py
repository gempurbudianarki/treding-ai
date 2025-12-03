from dataclasses import dataclass
from typing import Dict, Any, Optional

import MetaTrader5 as mt5
from loguru import logger

from config.settings import settings


@dataclass
class RiskDecision:
    allowed: bool
    lot: float
    reason: str


class RiskGovernor:
    """
    Polisi risk. Tugas:
    - tentukan lot
    - blokir trade kalau risk terlalu tinggi
    """

    def __init__(self) -> None:
        self.risk_pct = settings.RISK_PER_TRADE_PCT
        self.max_daily_dd_pct = settings.MAX_DAILY_DRAWDOWN_PCT
        self.max_open_trades = settings.MAX_OPEN_TRADES

    def _count_open_trades(self, symbol: str) -> int:
        positions = mt5.positions_get(symbol=symbol)
        if positions is None:
            return 0
        return len(positions)

    def _calc_lot_from_risk(
        self,
        symbol: str,
        equity: float,
        sl_pips: float,
    ) -> float:
        """
        Kalkulasi sangat sederhana:
        - risk dollar = equity * risk_pct
        - lot = risk_dollar / (sl_pips * tick_value)
        NB: ini kasar, nanti bisa diperhalus.
        """
        if sl_pips <= 0:
            return 0.0

        symbol_info = mt5.symbol_info(symbol)
        if not symbol_info:
            logger.error("RiskGovernor: gagal ambil symbol_info.")
            return 0.0

        # Asumsi kasar: tick_value = contract_size * tick_size
        tick_value = symbol_info.trade_contract_size * symbol_info.point
        risk_dollar = equity * (self.risk_pct / 100.0)
        lot = risk_dollar / (sl_pips * tick_value)
        lot = max(symbol_info.volume_min, min(lot, symbol_info.volume_max))
        return float(lot)

    def evaluate(
        self,
        symbol: str,
        sl_pips: float,
        daily_pl_pct: Optional[float],
    ) -> RiskDecision:
        account = mt5.account_info()
        if not account:
            logger.error("RiskGovernor: gagal ambil account_info.")
            return RiskDecision(False, 0.0, "no_account")

        equity = account.equity

        # cek daily drawdown
        if daily_pl_pct is not None and daily_pl_pct <= -self.max_daily_dd_pct:
            logger.warning(
                "RiskGovernor: daily drawdown {}% melewati limit {}%",
                daily_pl_pct,
                self.max_daily_dd_pct,
            )
            return RiskDecision(False, 0.0, "max_daily_drawdown_reached")

        # cek open trades
        open_trades = self._count_open_trades(symbol)
        if open_trades >= self.max_open_trades:
            logger.warning(
                "RiskGovernor: open trades {} >= max {}",
                open_trades,
                self.max_open_trades,
            )
            return RiskDecision(False, 0.0, "too_many_open_trades")

        lot = self._calc_lot_from_risk(symbol, equity, sl_pips)
        if lot <= 0:
            return RiskDecision(False, 0.0, "invalid_lot")

        return RiskDecision(True, lot, "ok")
