from typing import Dict, Any

from loguru import logger


class Orchestrator:
    """
    Ngegabungin semua otak:
    - technical_result
    - sentiment_result
    - condition_result

    Output: sinyal final:
    {
      "action": "BUY" / "SELL" / "HOLD",
      "reason": "....",
      "sl_pips": float,
      "tp_pips": float
    }
    """

    def decide(
        self,
        technical: Dict[str, Any],
        sentiment: Dict[str, Any],
        condition: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not condition.get("tradable", False):
            reason = f"market_not_tradable:{condition.get('reason')}"
            logger.info("Orchestrator: HOLD karena {}", reason)
            return {"action": "HOLD", "reason": reason, "sl_pips": 0.0, "tp_pips": 0.0}

        tech_dir = technical.get("direction", "neutral")
        tech_conf = float(technical.get("confidence", 0.0))
        sent = sentiment.get("sentiment", "neutral")
        sent_conf = float(sentiment.get("confidence", 0.0))

        # basic logic:
        # - butuh technical_conf minimal 0.4
        # - kombinasikan dengan sentiment

        if tech_conf < 0.4:
            logger.info("Orchestrator: HOLD karena technical confidence rendah ({})", tech_conf)
            return {"action": "HOLD", "reason": "low_technical_confidence", "sl_pips": 0.0, "tp_pips": 0.0}

        # mapping arah
        if tech_dir == "bullish":
            if sent == "bearish" and sent_conf >= 0.5:
                logger.info("Orchestrator: HOLD, technical bullish tapi sentiment bearish kuat.")
                return {"action": "HOLD", "reason": "conflict_tech_sentiment", "sl_pips": 0.0, "tp_pips": 0.0}
            action = "BUY"
        elif tech_dir == "bearish":
            if sent == "bullish" and sent_conf >= 0.5:
                logger.info("Orchestrator: HOLD, technical bearish tapi sentiment bullish kuat.")
                return {"action": "HOLD", "reason": "conflict_tech_sentiment", "sl_pips": 0.0, "tp_pips": 0.0}
            action = "SELL"
        else:
            logger.info("Orchestrator: HOLD, technical neutral.")
            return {"action": "HOLD", "reason": "technical_neutral", "sl_pips": 0.0, "tp_pips": 0.0}

        # SL/TP pips sederhana
        # nanti kita bisa bikin lebih pintar
        sl_pips = 300.0  # misal 300 "point" (bisa disesuaikan dengan symbol)
        tp_pips = 600.0

        logger.info(
            "Orchestrator: action={}, tech_dir={}, sent={}, tech_conf={}, sent_conf={}",
            action,
            tech_dir,
            sent,
            tech_conf,
            sent_conf,
        )

        return {
            "action": action,
            "reason": f"tech_{tech_dir}_sent_{sent}",
            "sl_pips": sl_pips,
            "tp_pips": tp_pips,
        }
