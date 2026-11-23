"""Stdlib-only clients: Sprites gateway (GitHub, OpenRouter)."""
import json
import urllib.request
import urllib.error

from . import config


class GatewayError(RuntimeError):
    pass


def _call(base, path, payload=None, method=None, timeout=30):
    url = base.rstrip("/") + "/" + path.lstrip("/")
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method or ("POST" if data else "GET"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        raise GatewayError(f"{e.code} {url}: {detail}") from e
    except Exception as e:
        raise GatewayError(f"{url}: {e}") from e


# --- GitHub ---

def gh_search_issues(query, per_page=10):
    import urllib.parse
    q = urllib.parse.urlencode({"q": query, "sort": "updated", "order": "desc", "per_page": per_page})
    return _call(config.GITHUB_GATEWAY, f"/search/issues?{q}")


def gh_me():
    return _call(config.GITHUB_GATEWAY, "/user")


def gh_comment(owner_repo, issue_number, body):
    return _call(
        config.GITHUB_GATEWAY,
        f"/repos/{owner_repo}/issues/{issue_number}/comments",
        {"body": body},
        method="POST",
    )


# --- OpenRouter ---

def chat(messages, model=None, max_tokens=500):
    return _call(
        config.LLM_GATEWAY,
        "/v1/chat/completions",
        {"model": model or config.MODEL, "messages": messages, "max_tokens": max_tokens},
        timeout=60,
    )
