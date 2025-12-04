from flask import Flask, render_template, jsonify, request
import json
from pathlib import Path

app = Flask(__name__)

STATUS_FILE = Path("../data/status.json")
CONTROL_FILE = Path("../data/control.json")


def load_json(path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except:
        return None


@app.route("/")
def overview():
    status = load_json(STATUS_FILE)
    control = load_json(CONTROL_FILE)
    return render_template("dashboard.html", status=status, control=control)


@app.route("/api/toggle", methods=["POST"])
def toggle_trading():
    data = load_json(CONTROL_FILE) or {}
    data["trading_enabled"] = bool(request.json.get("value"))
    CONTROL_FILE.write_text(json.dumps(data, indent=4))
    return jsonify({"ok": True})


@app.route("/api/mode", methods=["POST"])
def change_mode():
    mode = request.json.get("mode")
    data = load_json(CONTROL_FILE) or {}
    data["mode"] = mode
    CONTROL_FILE.write_text(json.dumps(data, indent=4))
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(port=5000, debug=True)
