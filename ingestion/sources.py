"""Live NBA Stats fetchers.

Each function returns a list[dict] in a normalized shape that matches what
ingestion.run expects. None of these are perfect — NBA Stats endpoints rotate
on us — but they're enough for an MVP refresh. Failures fall through to the
offline sample so the build never breaks.
"""
from __future__ import annotations

from typing import Iterable

from . import nba_api


def fetch_per_game_stats(season: str = "2024-25") -> list[dict]:
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


def fetch_last10_mpg(season: str = "2024-25") -> dict[int, float]:
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


def fetch_team_pace(season: str = "2024-25") -> dict[str, float]:
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
    paces = {r["TEAM_ABBREVIATION"]: r.get("PACE", 100.0) for r in rows}
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
