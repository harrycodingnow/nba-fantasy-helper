"""Live NBA Stats fetchers.

Each function returns a list[dict] in a normalized shape that matches what
ingestion.run expects. None of these are perfect — NBA Stats endpoints rotate
on us — but they're enough for an MVP refresh. Failures fall through to the
offline sample so the build never breaks.
"""
from __future__ import annotations

import os
from typing import Iterable

from . import nba_client as nba_api

# Season default. Overridable via $NBA_SEASON or per-call arg.
# NBA season string format: "YYYY-YY" (e.g. "2025-26" = season starting Oct 2025).
DEFAULT_SEASON = os.environ.get("NBA_SEASON", "2025-26")


def fetch_per_game_stats(season: str = DEFAULT_SEASON) -> list[dict]:
    """LeagueDashPlayerStats per-game per-mode."""
    payload = nba_api.fetch(
        "leaguedashplayerstats",
        {
            "Season": season,
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
            "MeasureType": "Base",
            "LastNGames": 0,
            "Month": 0,
            "OpponentTeamID": 0,
            "Period": 0,
            "PlayerExperience": "",
            "PlayerPosition": "",
            "PORound": 0,
            "ShotClockRange": "",
            "TeamID": 0,
            "VsConference": "",
            "VsDivision": "",
            "PaceAdjust": "N",
            "PlusMinus": "N",
            "Rank": "N",
            "Outcome": "",
            "Location": "",
            "GameSegment": "",
            "DateFrom": "",
            "DateTo": "",
            "DraftPick": "",
            "DraftYear": "",
            "GameScope": "",
            "Height": "",
            "College": "",
            "Country": "",
            "Conference": "",
            "Division": "",
            "StarterBench": "",
            "TwoWay": 0,
            "Weight": "",
            "ISTRound": "",
        },
    )
    rows = nba_api.rows_from_resultset(payload)
    out: list[dict] = []
    for r in rows:
        out.append({
            "id": r.get("PLAYER_ID"),
            "name": r.get("PLAYER_NAME"),
            "team": r.get("TEAM_ABBREVIATION"),
            "PTS": r.get("PTS", 0),
            "REB": r.get("REB", 0),
            "AST": r.get("AST", 0),
            "STL": r.get("STL", 0),
            "BLK": r.get("BLK", 0),
            "TOV": r.get("TOV", 0),
            "FG3M": r.get("FG3M", 0),
            "season_mpg": r.get("MIN", 0.0),
            "games_played": r.get("GP", 0),
        })
    return out


def fetch_last10_mpg(season: str = DEFAULT_SEASON) -> dict[int, float]:
    payload = nba_api.fetch(
        "leaguedashplayerstats",
        {
            "Season": season,
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
            "MeasureType": "Base",
            "LastNGames": 10,
            "Month": 0,
            "OpponentTeamID": 0,
            "Period": 0,
            "PORound": 0,
            "TeamID": 0,
            "PaceAdjust": "N",
            "PlusMinus": "N",
            "Rank": "N",
        },
    )
    rows = nba_api.rows_from_resultset(payload)
    return {r["PLAYER_ID"]: r.get("MIN", 0.0) for r in rows}


def fetch_team_pace(season: str = DEFAULT_SEASON) -> dict[str, float]:
    payload = nba_api.fetch(
        "leaguedashteamstats",
        {
            "Season": season,
            "SeasonType": "Regular Season",
            "PerMode": "PerGame",
            "MeasureType": "Advanced",
            "PaceAdjust": "N",
            "PlusMinus": "N",
            "Rank": "N",
            "LastNGames": 0,
            "Month": 0,
            "OpponentTeamID": 0,
            "Period": 0,
            "PORound": 0,
            "TeamID": 0,
        },
    )
    rows = nba_api.rows_from_resultset(payload)
    # leaguedashteamstats Advanced returns TEAM_ID + TEAM_NAME but no abbreviation.
    # Map via swar's static teams index so the resulting dict is keyed by abbr to
    # match how player rows reference their team.
    from nba_api.stats.static import teams as _teams
    id_to_abbr = {t["id"]: t["abbreviation"] for t in _teams.get_teams()}
    paces = {}
    for r in rows:
        abbr = id_to_abbr.get(r.get("TEAM_ID"))
        if abbr:
            paces[abbr] = r.get("PACE", 100.0)
    if not paces:
        return {}
    vals = sorted(paces.values())
    n = len(vals)

    def pct(v: float) -> float:
        rank = sum(1 for x in vals if x <= v)
        return rank / n

    return {team: round(pct(p), 3) for team, p in paces.items()}


def safe(call, default):
    """Call a fetcher, return default + log on any failure (network, schema)."""
    try:
        return call()
    except Exception as exc:  # noqa: BLE001
        print(f"  ! {call.__name__ if hasattr(call, '__name__') else 'fetch'} failed: {exc}")
        return default
