"""Ingestion entry point.

Pulls live data (or uses bundled offline sample), runs both engines, and
writes flat JSON snapshots into web/public/data/ for the static site to read.

Usage:
    python -m ingestion.run               # live refresh
    python -m ingestion.run --offline     # use bundled sample data
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from . import engines, sample_data, sources

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "web" / "public" / "data"
INJURIES_FILE = ROOT / "ingestion" / "data" / "injuries.json"


def _ensure_dirs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    INJURIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not INJURIES_FILE.exists():
        INJURIES_FILE.write_text(json.dumps(sample_data.offline_injuries(), indent=2))


def _load_injuries() -> dict[int, dict]:
    if not INJURIES_FILE.exists():
        return {}
    rows = json.loads(INJURIES_FILE.read_text())
    return {int(r["player_id"]): r for r in rows}


def _gather_live() -> tuple[list[dict], dict]:
    """Pull live data and merge it down into the same shape as offline_players()."""
    print("→ fetching league per-game stats")
    base = sources.safe(sources.fetch_per_game_stats, [])
    print(f"  {len(base)} player rows")

    print("→ fetching last-10 minutes")
    last10 = sources.safe(sources.fetch_last10_mpg, {})

    print("→ fetching team pace percentiles")
    pace_pct = sources.safe(sources.fetch_team_pace, {})

    injuries = _load_injuries()
    print(f"→ injuries: {len(injuries)} entries from {INJURIES_FILE.name}")

    merged: list[dict] = []
    for r in base:
        pid = r["id"]
        team = r["team"]
        fppg = engines.fantasy_points(r)
        season_mpg = float(r.get("season_mpg", 0.0)) or 0.0
        last10_mpg = float(last10.get(pid, season_mpg))
        inj = injuries.get(pid, {})
        merged.append({
            "id": pid,
            "name": r["name"],
            "team": team,
            "position": "",  # NBA Stats per-game endpoint doesn't include — use BR scrape later
            "fppg_last_season": fppg,
            "status": inj.get("status", "healthy"),
            "games_last_30d": min(int(r.get("games_played", 0)), 15),  # crude proxy
            "usage_rate": 0.20,  # default until we wire MeasureType=Advanced
            "team_pace_pct": float(pace_pct.get(team, 0.5)),
            "last10_mpg": last10_mpg,
            "season_mpg": season_mpg,
            "depth_rank": 2,  # default until depth chart wired
            "projected_minutes": last10_mpg or season_mpg,
            "fpts_per_minute": (fppg / season_mpg) if season_mpg else 0.0,
            "games_this_week": 3,
            "starter_out": False,
            "mpg_delta_last_3": 0.0,
        })

    schedule = {
        "week_start": datetime.now(timezone.utc).date().isoformat(),
        "week_end": None,
        "games_per_team": {},
        "_note": "live schedule fetcher TODO; using neutral 3-game default",
    }
    return merged, schedule


def _gather_offline() -> tuple[list[dict], dict]:
    return sample_data.offline_players(), sample_data.offline_schedule()


def run(offline: bool = False) -> None:
    _ensure_dirs()

    if offline:
        print("→ OFFLINE mode: using bundled sample data")
        players, schedule = _gather_offline()
    else:
        try:
            players, schedule = _gather_live()
            if not players:
                raise RuntimeError("live fetch returned 0 players")
        except Exception as exc:  # noqa: BLE001
            print(f"! live fetch failed ({exc}); falling back to offline sample")
            players, schedule = _gather_offline()

    # apply schedule to games_this_week if available
    games_per_team = schedule.get("games_per_team") or {}
    if games_per_team:
        for p in players:
            p["games_this_week"] = int(games_per_team.get(p["team"], p.get("games_this_week", 3)))

    # compute engines
    player_values = [engines.player_value_to_dict(engines.compute_player_value(p)) for p in players]
    opportunities = [engines.opportunity_to_dict(engines.compute_opportunity(p)) for p in players]

    # sort
    player_values.sort(key=lambda d: d["dynamic_value"], reverse=True)
    opportunities.sort(key=lambda d: d["weekly_value"], reverse=True)

    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "format": "points",
        "source_mode": "offline" if offline else "live",
        "schedule": schedule,
        "counts": {
            "players": len(player_values),
            "opportunities": len(opportunities),
        },
    }

    (OUT_DIR / "players.json").write_text(json.dumps(player_values, indent=2))
    (OUT_DIR / "opportunities.json").write_text(json.dumps(opportunities, indent=2))
    (OUT_DIR / "snapshot.json").write_text(json.dumps(snapshot, indent=2))
    (OUT_DIR / "injuries.json").write_text(json.dumps(list(_load_injuries().values()), indent=2))

    print(f"✓ wrote {len(player_values)} player values, {len(opportunities)} opportunities → {OUT_DIR}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--offline", action="store_true", help="use bundled sample data, no network")
    args = p.parse_args()
    run(offline=args.offline)


if __name__ == "__main__":
    main()
