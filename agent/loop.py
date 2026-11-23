"""Gravy cycle: watch (GitHub connector) -> screen (OpenRouter) -> deliver (own repo) -> ledger."""
import json
import re
import time

from . import config, gateway, ledger

# gpt-4o-mini fallback rates, USD per 1M tokens (если провайдер не вернул usage.cost)
FALLBACK_RATES = {"input": 0.15, "output": 0.60}


def _estimate_cost(resp):
    usage = (resp or {}).get("usage") or {}
    if usage.get("cost") is not None:
        return float(usage["cost"])
    pin = float(usage.get("prompt_tokens") or 0)
    pout = float(usage.get("completion_tokens") or 0)
    return (pin * FALLBACK_RATES["input"] + pout * FALLBACK_RATES["output"]) / 1e6


def watch():
    res = gateway.gh_search_issues(config.WATCH_QUERY, per_page=config.TOP_N)
    items = res.get("items") or []
    out = []
    for it in items:
        out.append(
            {
                "number": it.get("number"),
                "title": (it.get("title") or "")[:200],
                "url": it.get("html_url"),
                "repo": ((it.get("repository_url") or "").split("/repos/")[-1]),
                "comments": it.get("comments"),
                "updated_at": it.get("updated_at"),
            }
        )
    return out


def screen(items):
    if not items:
        return []
    blob = json.dumps(items, ensure_ascii=False)
    prompt = (
        "Ты — скринер платных возможностей для автономного агента, который делает "
        "аудиты, desk-research, автоматизацию и API-интеграции. Оцени каждую возможность "
        "по шкале 0-10 (fit): есть ли реальная работа и оплата, подходит ли профиль, "
        "нет ли очевидного мошенничества. Ответь СТРОГО JSON-массивом "
        '[{"idx":0,"fit":0-10,"reason":"<=120 симв","pitch":"<=180 симв"}] для ВСЕХ элементов.\n\n'
        + blob
    )
    resp = gateway.chat(
        [{"role": "user", "content": prompt}],
        max_tokens=900,
    )
    cost = _estimate_cost(resp)
    text = resp["choices"][0]["message"]["content"]
    m = re.search(r"\[.*\]", text, re.S)
    scored = json.loads(m.group(0)) if m else []
    for s in scored:
        s["cost_usd"] = cost / max(len(scored), 1)
        s["item"] = items[s["idx"]] if 0 <= s.get("idx", -1) < len(items) else None
    return scored


def deliver(scored):
    """Отчёт о скрининге уходит комментарием в СОБСТВЕННЫЙ репозиторий (issue #1 work log)."""
    ok = [s for s in scored if s.get("item") and float(s.get("fit", 0)) >= config.FIT_THRESHOLD]
    lines = [
        f"### Gravy screen {time.strftime('%Y-%m-%d %H:%MZ', time.gmtime())}",
        f"query: `{config.WATCH_QUERY}` | model: {config.MODEL} | top-fit ≥ {config.FIT_THRESHOLD}: {len(ok)}",
        "",
    ]
    for s in sorted(scored, key=lambda x: -float(x.get("fit", 0))):
        it = s.get("item") or {}
        mark = "✅" if float(s.get("fit", 0)) >= config.FIT_THRESHOLD else "·"
        lines.append(
            f"{mark} **fit {s.get('fit')}** [{it.get('title','?')}]({it.get('url','')}) — {s.get('reason','')}"
        )
    body = "\n".join(lines)
    try:
        ref = gateway.gh_comment("pyfile-toolkit/gravy", 1, body)
        ref_url = (ref or {}).get("html_url")
        ledger.record_action("screen_report", f"{len(scored)} scored, {len(ok)} top-fit", ref_url)
        return ref_url, ok
    except gateway.GatewayError as e:
        # issue #1 может не существовать — создаём и повторяем один раз
        if "404" in str(e):
            gateway._call(
                config.GITHUB_GATEWAY,
                "/repos/pyfile-toolkit/gravy/issues",
                {"title": "Gravy work log (auto)", "body": "Automated delivery log."},
                method="POST",
            )
            ref = gateway.gh_comment("pyfile-toolkit/gravy", 1, body)
            ref_url = (ref or {}).get("html_url")
            ledger.record_action("screen_report", f"{len(scored)} scored, {len(ok)} top-fit", ref_url)
            return ref_url, ok
        ledger.record_action("screen_report_error", str(e)[:200])
        return None, ok


def cycle():
    t0 = time.time()
    ledger.record_action("cycle_start", config.WATCH_QUERY)
    items = watch()
    ledger.record_action("watch", f"{len(items)} items")
    scored = screen(items)
    spent = sum(float(s.get("cost_usd", 0)) for s in scored)
    if spent > 0:
        ledger.add_entry("spent", spent, f"screening {len(items)} items via {config.MODEL}", "openrouter")
    ref, ok = deliver(scored)
    summary = {
        "watched": len(items),
        "scored": len(scored),
        "top_fit": len(ok),
        "llm_spent_usd": round(spent, 6),
        "report": ref,
        "seconds": round(time.time() - t0, 1),
    }
    ledger.record_action("cycle_done", json.dumps(summary))
    return summary


if __name__ == "__main__":
    print(json.dumps(cycle(), indent=1))
