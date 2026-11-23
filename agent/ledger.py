"""Ledger: честный учёт. Прошлый опыт агента — отдельным carried-блоком
с источником, новые события — отдельными записями. Ничего не выдумываем."""
import json
import os
import time

from . import config

CARRIED = {
    "note": "30-day history of this same agent before it moved to a Sprite",
    "revenue_usd_approx": 11.1,
    "costs_usd_approx": 1.7,
    "source": "public Nano/Base/Lightning transaction log + platform receipts (Nov 2026)",
    "inference_cost": "unknown, excluded",
}


def _load(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, path)


def load_ledger():
    led = _load(config.LEDGER_PATH, {"carried": CARRIED, "entries": []})
    led.setdefault("carried", CARRIED)
    led.setdefault("entries", [])
    return led


def add_entry(kind, amount_usd, note, source):
    """kind: 'earned' | 'spent'"""
    led = load_ledger()
    led["entries"].append(
        {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "kind": kind,
            "amount_usd": round(float(amount_usd), 6),
            "note": note,
            "source": source,
        }
    )
    _save(config.LEDGER_PATH, led)
    return led


def totals():
    led = load_ledger()
    earned = sum(e["amount_usd"] for e in led["entries"] if e["kind"] == "earned")
    spent = sum(e["amount_usd"] for e in led["entries"] if e["kind"] == "spent")
    return {
        "carried": led["carried"],
        "live_earned_usd": round(earned, 6),
        "live_spent_usd": round(spent, 6),
        "live_net_usd": round(earned - spent, 6),
        "entries": len(led["entries"]),
    }


def record_action(action, detail, ref=None):
    acts = _load(config.ACTIONS_PATH, [])
    acts.append(
        {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "action": action,
            "detail": detail,
            "ref": ref,
        }
    )
    _save(config.ACTIONS_PATH, acts[-100:])


def load_actions():
    return _load(config.ACTIONS_PATH, [])
