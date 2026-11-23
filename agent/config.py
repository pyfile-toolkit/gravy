"""Gravy config: gateway endpoints (org connection ids are not secrets —
the gateway authenticates the calling Sprite, not the URL)."""
import os

SPRITE_NAME = os.environ.get("SPRITE_NAME", "gravy")

GITHUB_GATEWAY = os.environ.get(
    "GITHUB_GATEWAY",
    "https://api.sprites.dev/v1/gateway/github/pzMtbJZnsfV6z5uhuV-MFQ",
)
OPENROUTER_GATEWAY = os.environ.get(
    "OPENROUTER_GATEWAY",
    "https://api.sprites.dev/v1/gateway/openrouter/-45-yWPGQvqs8b0AhwYibQ",
)

# Скрининг возможностей: модель и порог пригодности
MODEL = os.environ.get("GRAVY_MODEL", "openai/gpt-4o-mini")
FIT_THRESHOLD = float(os.environ.get("GRAVY_FIT_THRESHOLD", "7.0"))
TOP_N = int(os.environ.get("GRAVY_TOP_N", "5"))

# Источник возможностей: GitHub search query (read-only)
WATCH_QUERY = os.environ.get(
    "GRAVY_WATCH_QUERY",
    'bounty label:"$" state:open sort:updated',
)

STATE_DIR = os.environ.get("GRAVY_STATE_DIR", "state")
LEDGER_PATH = os.path.join(STATE_DIR, "ledger.json")
ACTIONS_PATH = os.path.join(STATE_DIR, "actions.json")
