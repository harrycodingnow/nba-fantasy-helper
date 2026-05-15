# NBA Fantasy Helper

Two-engine fantasy NBA decision tool, points league only (v1).

- **Player Value Engine** — `dynamic_value = base_value × injury_risk_factor × opportunity_factor × minutes_factor × roster_factor`. Surfaces a live ranking + risk label per player, with the multiplier breakdown exposed in the UI.
- **Opportunity Engine** — `weekly_value = projected_minutes × fpts_per_minute × games_this_week × opportunity_boost`. Detects lineup shifts from injuries (backup minutes jump) and weights by games-this-week (2 vs 4 game weeks).

## Stack

- `ingestion/` — Python 3. Pulls per-game player stats + injury report + depth charts + weekly schedule from public NBA Stats API endpoints. Computes both engines. Emits flat JSON snapshots to `web/public/data/`.
- `web/` — Next.js 14, fully static (`output: "export"`). Reads JSON from `/data/*.json` at build time + runtime fetch. Tailwind-free, plain CSS modules.
- Hosting: GitHub Pages via `.github/workflows/deploy.yml` on push to `main`.

## Run locally

```bash
# 1. Refresh data (writes web/public/data/*.json)
cd ingestion
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m ingestion.run                 # full refresh
python -m ingestion.run --offline       # use bundled sample data (no network)

# 2. Dev the site
cd ../web
npm install
npm run dev          # http://localhost:3000

# 3. Build static export
npm run build        # outputs ./out/
```

## Refresh cadence

NBA Stats API is unofficial and rate-limited. Refresh manually before drafts; nightly during the season is plenty for the streamer view. The Python CLI sleeps 600ms between requests and caches raw responses in `ingestion/.cache/` keyed by date.

## Data sources

| Source | What | Endpoint |
|---|---|---|
| stats.nba.com | per-game player stats, season totals | `/stats/leaguedashplayerstats`, `/stats/playergamelog` |
| stats.nba.com | weekly schedule | `/stats/scheduleleaguev2` |
| Basketball Reference | depth charts (fallback) | scraped tables |
| Local JSON | injury report | `ingestion/data/injuries.json` (manual update — public NBA injury API is locked behind auth) |

## Known limitations (v1)

- Points-league only. 9-cat / roto deferred.
- No live in-game updates.
- No league sync (ESPN / Yahoo / Sleeper).
- Single user, no auth, no DB. Flat JSON snapshots only.
- Injury report is manually curated in `ingestion/data/injuries.json` because NBA's official report is a PDF and rotowire/espn require scraping that breaks often. Each entry: `{player_id, status, expected_return, severity}`.
- Depth chart scraper falls back to a baked-in heuristic (top-2 minutes leaders per team per position) when network unavailable.

## Multiplier reference

All multipliers are documented in `ingestion/engines.py` with their bands:

| Factor | Range | Driver |
|---|---|---|
| `injury_risk_factor` | 0.5 – 1.05 | injury status (out, gtd, healthy) + 30-day games played |
| `opportunity_factor` | 0.85 – 1.30 | usage rate × team-pace percentile |
| `minutes_factor` | 0.7 – 1.20 | last-10 MPG vs season MPG (trend) |
| `roster_factor` | 0.9 – 1.15 | depth-chart rank (1 = starter) |

## Deploy

Push to `main`. The GitHub Action runs `python -m ingestion.run --offline` (so the action doesn't hit NBA's API from CI) and `npm run build`, then publishes `web/out/` to Pages. To deploy with fresh data, run ingestion locally, commit `web/public/data/*.json`, then push.

See [DECISIONS.md](DECISIONS.md) for the MVP scope rationale.
