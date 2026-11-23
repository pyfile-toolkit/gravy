# 🥧 Gravy

**A personal agent that pays its own rent.**

Gravy is my autonomous agent, now living on a [Fly Sprite](https://fly.io/sprites/) — a
hardware-isolated Linux box that sleeps when idle and costs nothing while asleep. It watches
for paid opportunities through the **GitHub connector**, screens them with an LLM through the
**OpenRouter connector** (both calls go through the Sprites gateway — the Sprite never holds a
credential), delivers its screening report back to this repo, and keeps a **ledger** of what it
earns and spends.

Gravy didn't start from zero: the same agent earned **~$11 in revenue over 30 days** on real
markets (x402 pay-per-call API, Subnano content sales, escrowed task markets) before moving in
here. That carried history is shown on the dashboard, labeled with its source. Everything new
is recorded live.

## How it works

```
┌─────────────── Sprite: gravy ────────────────┐
│  loop.py                                     │
│   1. watch   → GitHub gateway /search/issues │  (read-only, connector)
│   2. screen  → OpenRouter gateway /chat      │  (managed connector)
│   3. deliver → comment report on issue #1    │  (write, connector)
│   4. ledger  → state/ledger.json             │
│  dashboard.py → http://:8080 (Sprite URL)    │
└──────────────────────────────────────────────┘
         │ gateway (token never enters the Sprite)
         ▼
   GitHub API · OpenRouter API
```

- **Connectors, not keys.** Every external call goes through
  `https://api.sprites.dev/v1/gateway/<provider>/<connection_id>/…`. The gateway authenticates
  the calling Sprite, checks the org access policy (deny-by-default; ours is `name_prefix=gravy`),
  and attaches the stored credential. The Sprite only knows URLs.
- **Honest ledger.** Carried history and live entries are separate; LLM spend is recorded from
  actual API usage each cycle; nothing is inflated.

## Run

```sh
./run.sh          # dashboard + one cycle
./run.sh loop     # dashboard + cycle every GRAVY_INTERVAL seconds (default 1800)
```

Zero dependencies beyond Python 3 stdlib.

## Status (Hacksgiving, day 1)

- [x] Sprite `gravy` created, Pi/node/python3 preinstalled
- [x] GitHub connector (OAuth, `repo`+`read:org`) — verified live (`GET /user` via gateway)
- [x] OpenRouter managed connector — verified (`/v1/chat/completions` via gateway)
- [x] Cycle: watch → screen → deliver → ledger; dashboard on :8080
- [ ] Live demo recording + X post
- [ ] Submission

Built for [Fly.io Hacksgiving](https://fly.io/hacksgiving) (Nov 23–29, 2026).
