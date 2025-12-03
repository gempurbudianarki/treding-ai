from typing import Dict, Any

import numpy as np
import pandas as pd
from loguru import logger


class ConditionBrain:
    """
    Cek kondisi market:
    - volatilitas
    - choppy atau tidak (sangat sederhana dulu)
    """

    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df is None or df.empty:
            logger.warning("ConditionBrain: DataFrame kosong.")
            return {"tradable": False, "reason": "no_data", "info": {}}

        recent = df.tail(50)
        ranges = recent["high"] - recent["low"]
        avg_range = ranges.mean()
        std_range = ranges.std()

        # bandingkan range dengan harga
        last_close = recent["close"].iloc[-1]
        vol_ratio = avg_range / last_close

        tradable = True
        reason = "ok"

        if vol_ratio < 0.001:
            tradable = False
            reason = "too_flat"
        elif vol_ratio > 0.01:
            tradable = False
            reason = "too_volatile"

        info = {
            "avg_range": float(avg_range),
            "std_range": float(std_range),
            "vol_ratio": float(vol_ratio),
        }

        logger.debug("ConditionBrain: tradable={}, reason={}", tradable, reason)
        return {"tradable": tradable, "reason": reason, "info": info}
