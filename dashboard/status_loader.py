from pathlib import Path
import json
from typing import Any, Dict

STATUS_FILE = Path("data/status.json")
CONTROL_FILE = Path("data/control.json")
HISTORY_FILE = Path("data/history.json")


def _read_json(path: Path) -> Dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(text)
    except Exception:
        return None


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_status() -> Dict[str, Any] | None:
    """
    Normalisasi status.json supaya aman diakses di template.
    Struktur final:
    {
      "timestamp": str,
      "symbol": str,
      "timeframe_minutes": int,
      "dry_run": bool,
      "mode": str,
      "technical": {"direction": str, "confidence": float},
      "sentiment": {"sentiment": str, "confidence": float, "headlines": [str]},
      "decision": {"action": str, "reason": str},
    }
    """
    raw = _read_json(STATUS_FILE)
    if not raw:
        return None

    technical = raw.get("technical") or {}
    sentiment = raw.get("sentiment") or {}
    decision = raw.get("decision") or {}

    headlines = sentiment.get("headlines") or []
    # Paksa headlines jadi list[str]
    if isinstance(headlines, str):
        headlines = [headlines]
    elif not isinstance(headlines, list):
        headlines = []

    normalized: Dict[str, Any] = {
        "timestamp": raw.get("timestamp", "-"),
        "symbol": raw.get("symbol", "-"),
        "timeframe_minutes": int(raw.get("timeframe_minutes", 0) or 0),
        "dry_run": bool(raw.get("dry_run", True)),
        "mode": (raw.get("mode") or raw.get("trading_mode") or "SAFE").upper(),
        "technical": {
            "direction": str(technical.get("direction", "neutral")).lower(),
            "confidence": float(technical.get("confidence", 0.0) or 0.0),
        },
        "sentiment": {
            "sentiment": str(sentiment.get("sentiment", "neutral")).lower(),
            "confidence": float(sentiment.get("confidence", 0.0) or 0.0),
            "headlines": [str(h) for h in headlines],
        },
        "decision": {
            "action": str(decision.get("action", "HOLD")).upper(),
            "reason": str(decision.get("reason", "-")),
        },
    }
    return normalized


def load_control() -> Dict[str, Any]:
    """
    control.json buat ON/OFF bot + mode pilih dari dashboard.
    Format:
    {
      "trading_enabled": bool,
      "mode": "SAFE" | "BALANCED" | "AGGRESSIVE" | "SCALPING_M5"
    }
    """
    existing = _read_json(CONTROL_FILE) or {}
    trading_enabled = bool(existing.get("trading_enabled", False))
    mode = str(existing.get("mode", "SAFE")).upper()

    data = {
        "trading_enabled": trading_enabled,
        "mode": mode,
    }
    _write_json(CONTROL_FILE, data)
    return data


def save_control(trading_enabled: bool | None = None, mode: str | None = None) -> Dict[str, Any]:
    current = load_control()
    if trading_enabled is not None:
        current["trading_enabled"] = bool(trading_enabled)
    if mode is not None:
        current["mode"] = mode.upper()
    _write_json(CONTROL_FILE, current)
    return current


def load_history() -> Dict[str, Any]:
    """
    history.json rencana isi:
    {
      "daily_pnl": [{"date": "2025-12-04", "pnl": 12.3}, ...],
      "weekly_pnl": [...],
      "signals": [
        {"time": "...", "symbol": "XAUUSD", "action": "BUY", "reason": "..."},
        ...
      ]
    }
    Kalau belum ada, balikin struktur kosong tapi aman buat UI.
    """
    raw = _read_json(HISTORY_FILE) or {}
    daily = raw.get("daily_pnl") or []
    weekly = raw.get("weekly_pnl") or []
    signals = raw.get("signals") or []

    return {
        "daily_pnl": daily if isinstance(daily, list) else [],
        "weekly_pnl": weekly if isinstance(weekly, list) else [],
        "signals": signals if isinstance(signals, list) else [],
    }
