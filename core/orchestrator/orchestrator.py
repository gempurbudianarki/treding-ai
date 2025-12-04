from loguru import logger
from core.utils.control_loader import load_control

class Orchestrator:
    def __init__(self):
        self.mode = "SAFE"
        self.conf_threshold = 0.35
        self.lot_size = 0.01

    def update_mode(self):
        control = load_control()
        self.mode = control["mode"].upper()

        if self.mode == "SAFE":
            self.conf_threshold = 0.40
            self.lot_size = 0.01

        elif self.mode == "BALANCED":
            self.conf_threshold = 0.30
            self.lot_size = 0.02

        elif self.mode == "AGGRESSIVE":
            self.conf_threshold = 0.20
            self.lot_size = 0.04

        elif self.mode == "SCALPING_M5":
            self.conf_threshold = 0.15
            self.lot_size = 0.03

        logger.info(f"MODE UPDATED: {self.mode}, threshold={self.conf_threshold}, lot={self.lot_size}")

    def decide(self, technical, sentiment, condition):
        self.update_mode()  # refresh mode tiap loop

        # trading disabled →
        control = load_control()
        if not control["trading_enabled"]:
            return {
                "action": "HOLD",
                "reason": "disabled_from_dashboard",
                "lot": 0
            }

        # check technical confidence
        if technical["confidence"] < self.conf_threshold:
            return {
                "action": "HOLD",
                "reason": "low_technical_confidence",
                "lot": 0
            }

        # decide buy/sell
        if technical["direction"] == "buy":
            return {
                "action": "BUY",
                "reason": "technical_signal_buy",
                "lot": self.lot_size
            }

        elif technical["direction"] == "sell":
            return {
                "action": "SELL",
                "reason": "technical_signal_sell",
                "lot": self.lot_size
            }

        return {
            "action": "HOLD",
            "reason": "neutral_no_signal",
            "lot": 0
        }
