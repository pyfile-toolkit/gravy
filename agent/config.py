"""Gravy config: gateway endpoints (org connection ids are not secrets —
the gateway authenticates the calling Sprite, not the URL)."""
import os

SPRITE_NAME = os.environ.get("SPRITE_NAME", "gravy")

GITHUB_GATEWAY = os.environ.get(
    "GITHUB_GATEWAY",
    "https://api.sprites.dev/v1/gateway/github/pzMtbJZnsfV6z5uhuV-MFQ",
)
# LLM: Groq free tier через Custom API connector (ключ хранится в коннекторе org,
# не в Sprite). OpenRouter managed подключён тоже, но prepaid limit $0.
LLM_GATEWAY = os.environ.get(
    "LLM_GATEWAY",
    "https://api.sprites.dev/v1/gateway/custom_api/orYq2zt0pwpnz7IAAVE9nw",
)

# Скрининг возможностей: модель и порог пригодности
MODEL = os.environ.get("GRAVY_MODEL", "qwen/qwen3.8-27b")
FIT_THRESHOLD = float(os.environ.get("GRAVY_FIT_THRESHOLD", "7.0"))
TOP_N = int(os.environ.get("GRAVY_TOP_N", "5"))

# Источник возможностей: GitHub search query (read-only)
WATCH_QUERY = os.environ.get(
    "GRAVY_WATCH_QUERY",
    'bounty state:open sort:updated',
)

STATE_DIR = os.environ.get("GRAVY_STATE_DIR", "state")
LEDGER_PATH = os.path.join(STATE_DIR, "ledger.json")
ACTIONS_PATH = os.path.join(STATE_DIR, "actions.json")
