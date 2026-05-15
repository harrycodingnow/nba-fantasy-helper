# MVP Decisions

Locked from kanban triage comment (worker, 2026-05-15):

- Stack: Next.js (static export) + Python ingestion CLI.
- Hosting: GitHub Pages on push to `main`. No backend server.
- Single user (Harry). No auth.
- Format: **points league only**. 9-cat / roto deferred.
- Data: free public NBA Stats API + Basketball Reference. No paid feeds.
- Storage: flat JSON snapshots committed to repo (or written to `web/public/data/`). No DB.
- Refresh: manual via `python -m ingestion.run`. Nightly is plenty during season.

Out of scope for v1:

- Live in-game updates
- ESPN/Yahoo/Sleeper league sync
- Native mobile (responsive web only)
- ML projections beyond rule-based multipliers

## Open items deferred past v1

- 9-cat / roto support — engines accept a `format` param but only `points` is implemented.
- Auto-scraper for ESPN injury report — currently a manual JSON file because of rate-limit / paywall friction.
- Persistence of historical snapshots for trend charts.
