import time
from datetime import datetime
from typing import Optional

import MetaTrader5 as mt5
from loguru import logger

from config.settings import settings
from core.feeder.mt5_feeder import MT5Feeder
from core.brains.technical_brain import TechnicalBrain
from core.brains.sentiment_brain import SentimentBrain
from core.brains.condition_brain import ConditionBrain
from core.risk.risk_governor import RiskGovernor
from core.execution.mt5_executor import MT5Executor
from core.orchestrator.orchestrator import Orchestrator


def setup_logger() -> None:
    log_path = "data/logs/bot.log"
    logger.add(log_path, rotation="5 MB", retention="7 days", level="INFO")
    logger.info("Logger initialized. Log file: {}", log_path)


def calc_sl_tp_price(
    symbol: str,
    entry_type: str,
    sl_pips: float,
    tp_pips: float,
) -> tuple[Optional[float], Optional[float]]:
    tick = mt5.symbol_info_tick(symbol)
    symbol_info = mt5.symbol_info(symbol)
    if not tick or not symbol_info:
        return None, None

    point = symbol_info.point

    if entry_type == "BUY":
        sl = tick.ask - sl_pips * point
        tp = tick.ask + tp_pips * point
    else:
        sl = tick.bid + sl_pips * point
        tp = tick.bid - tp_pips * point

    return sl, tp


def main() -> None:
    setup_logger()
    logger.info("Starting AI Trading Bot for symbol {}", settings.SYMBOL)

    feeder = MT5Feeder()
    if not feeder.initialize():
        logger.error("Gagal inisialisasi feeder. Keluar.")
        return

    technical_brain = TechnicalBrain()
    sentiment_brain = SentimentBrain()
    condition_brain = ConditionBrain()
    risk_governor = RiskGovernor()
    executor = MT5Executor(symbol=settings.SYMBOL)
    orchestrator = Orchestrator()

    logger.info("Loop dimulai. DRY_RUN={}, TIMEFRAME={}m", settings.DRY_RUN, settings.TIMEFRAME_MINUTES)

    try:
        while True:
            loop_start = datetime.now()
            logger.info("=== LOOP MULAI: {} ===", loop_start)

            df = feeder.get_history(bars=max(settings.MIN_BARS_REQUIRED, 300))
            if df is None or len(df) < settings.MIN_BARS_REQUIRED:
                logger.warning(
                    "Data belum cukup ({} bar < {}). Tidur sebentar.",
                    len(df) if df is not None else 0,
                    settings.MIN_BARS_REQUIRED,
                )
                time.sleep(settings.LOOP_SLEEP_SECONDS)
                continue

            # --- Otak teknikal ---
            technical_result = technical_brain.analyze(df)

            # --- Otak sentiment (sementara neutral sampai kita sambung news beneran) ---
            sentiment_result = sentiment_brain.analyze()


            # --- Otak kondisi market ---
            condition_result = condition_brain.analyze(df)

            # --- Keputusan utama ---
            decision = orchestrator.decide(technical_result, sentiment_result, condition_result)

            if decision["action"] == "HOLD":
                logger.info("HOLD: reason={}", decision["reason"])
            else:
                # hitung SL/TP price
                sl_price, tp_price = calc_sl_tp_price(
                    settings.SYMBOL,
                    decision["action"],
                    decision["sl_pips"],
                    decision["tp_pips"],
                )

                # daily P/L belum kita track detail -> set None dulu
                daily_pl_pct: Optional[float] = None

                # risk check
                risk_decision = risk_governor.evaluate(
                    symbol=settings.SYMBOL,
                    sl_pips=decision["sl_pips"],
                    daily_pl_pct=daily_pl_pct,
                )

                if not risk_decision.allowed:
                    logger.info(
                        "Trade diblokir oleh RiskGovernor: {}",
                        risk_decision.reason,
                    )
                else:
                    if decision["action"] == "BUY":
                        executor.buy_market(
                            lot=risk_decision.lot,
                            sl=sl_price,
                            tp=tp_price,
                            reason=decision["reason"],
                        )
                    elif decision["action"] == "SELL":
                        executor.sell_market(
                            lot=risk_decision.lot,
                            sl=sl_price,
                            tp=tp_price,
                            reason=decision["reason"],
                        )

            logger.info("=== LOOP SELESAI ===")
            time.sleep(settings.LOOP_SLEEP_SECONDS)

    except KeyboardInterrupt:
        logger.info("Bot dihentikan oleh user (CTRL+C).")
    finally:
        mt5.shutdown()
        logger.info("MT5 shutdown, bot selesai.")


if __name__ == "__main__":
    main()
