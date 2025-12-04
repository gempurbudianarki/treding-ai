from core.utils.control_loader import load_control
import MetaTrader5 as mt5

...

decision = orchestrator.decide(technical_result, sentiment_result, condition_result)

action = decision["action"]
lot = decision["lot"]
reason = decision["reason"]

logger.info(f"DECISION: {action} | lot={lot} | reason={reason}")

control = load_control()
if not control["trading_enabled"]:
    logger.info("Trading disabled from dashboard → HOLD")
else:
    if action == "BUY":
        mt5.order_send({
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": settings.SYMBOL,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "deviation": 10,
        })
        logger.info(f"EXECUTED BUY {lot}")

    elif action == "SELL":
        mt5.order_send({
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": settings.SYMBOL,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "deviation": 10,
        })
        logger.info(f"EXECUTED SELL {lot}")
