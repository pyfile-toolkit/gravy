"""Dashboard on :8080 (Sprite URL) — ledger + recent actions."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import ledger

PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Gravy</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{font-family:ui-sans-serif,system-ui,sans-serif;margin:0;background:#141210;color:#eee8dc}
.wrap{max-width:860px;margin:0 auto;padding:28px 18px}
h1{font-size:26px;margin:0 0 4px} h1 span{color:#e8b45a}
.sub{color:#9a917f;font-size:13px;margin-bottom:22px}
.cards{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:24px}
.card{background:#1e1b17;border:1px solid #332e26;border-radius:10px;padding:14px 18px;min-width:150px}
.card .v{font-size:24px;font-weight:700;color:#8fd19e} .card .v.neg{color:#e88f7a}
.card .k{font-size:11px;color:#9a917f;text-transform:uppercase;letter-spacing:.08em;margin-top:4px}
table{width:100%;border-collapse:collapse;font-size:13px}
td,th{padding:7px 8px;border-bottom:1px solid #2a261f;text-align:left;vertical-align:top}
th{color:#9a917f;font-size:11px;text-transform:uppercase}
.earned{color:#8fd19e} .spent{color:#e88f7a} .ts{color:#776f5f;white-space:nowrap}
a{color:#e8b45a} .tag{background:#2a261f;border-radius:6px;padding:1px 7px;font-size:11px;color:#c9bfa8}
h2{font-size:15px;margin:26px 0 8px;color:#c9bfa8}
.carried{background:#1a1815;border-left:3px solid #e8b45a;padding:10px 14px;font-size:13px;color:#b7ae9a;border-radius:0 8px 8px 0}
</style></head><body><div class="wrap">
<h1>🥧 <span>Gravy</span> — a personal agent that pays its own rent</h1>
<div class="sub">Hacksgiving entry · runs on a Fly Sprite · GitHub + OpenRouter connectors · live cycle below</div>
<div class="cards">
 <div class="card"><div class="v">__EARNED__</div><div class="k">live earned, USD</div></div>
 <div class="card"><div class="v neg">__SPENT__</div><div class="k">live spent, USD</div></div>
 <div class="card"><div class="v">__NET__</div><div class="k">live net, USD</div></div>
 <div class="card"><div class="v">__ENTRIES__</div><div class="k">ledger entries</div></div>
</div>
<div class="carried">Carried history: __CARRIED__ <b>(__CARRIED_SRC__)</b></div>
<h2>Recent actions</h2>
<table><tr><th>time</th><th>action</th><th>detail</th></tr>__ACTIONS__</table>
<h2>Ledger</h2>
<table><tr><th>time</th><th>kind</th><th>usd</th><th>note</th></tr>__LEDGER__</table>
</div></body></html>"""


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_response(404); self.end_headers(); return
        t = ledger.totals()
        rows_a = "".join(
            f'<tr><td class="ts">{_esc(a["ts"])}</td><td><span class="tag">{_esc(a["action"])}</span></td><td>{_esc(str(a.get("detail",""))[:220])}</td></tr>'
            for a in reversed(ledger.load_actions()[:15])
        ) or '<tr><td colspan=3>no actions yet</td></tr>'
        entries = ledger.load_ledger()["entries"]
        rows_l = "".join(
            f'<tr><td class="ts">{_esc(e["ts"])}</td><td class="{e["kind"]}">{e["kind"]}</td><td class="{e["kind"]}">{e["amount_usd"]:.6f}</td><td>{_esc(e["note"])}</td></tr>'
            for e in reversed(entries[-25:])
        ) or '<tr><td colspan=4>no live entries yet</td></tr>'
        c = t["carried"]
        html = (
            PAGE.replace("__EARNED__", f'{t["live_earned_usd"]:.4f}')
            .replace("__SPENT__", f'{t["live_spent_usd"]:.4f}')
            .replace("__NET__", f'{t["live_net_usd"]:.4f}')
            .replace("__ENTRIES__", str(t["entries"]))
            .replace("__CARRIED__", f'${c["revenue_usd_approx"]} revenue / ${c["costs_usd_approx"]} costs over 30 days')
            .replace("__CARRIED_SRC__", _esc(c["source"]))
            .replace("__ACTIONS__", rows_a)
            .replace("__LEDGER__", rows_l)
        )
        data = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


def main(host="0.0.0.0", port=8080):
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
