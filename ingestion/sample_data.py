"""Bundled offline sample dataset.

Used when --offline is passed (CI, no-network demo, or first-run sanity test).
A small but realistic slice: ~30 players across 8 teams + a 1-week schedule.
"""

OFFLINE_PLAYERS = [
    # id, name, team, position, fppg_last_season, status, games_last_30d,
    # usage_rate, team_pace_pct, last10_mpg, season_mpg, depth_rank,
    # projected_minutes, fpts_per_minute, games_this_week, starter_out,
    # mpg_delta_last_3
    (1629029, "Luka Doncic", "DAL", "PG", 58.4, "healthy", 12, 0.34, 0.55, 37.0, 36.5, 1, 37.0, 1.58, 4, False, 0.5),
    (203999, "Nikola Jokic", "DEN", "C",  61.2, "healthy", 13, 0.30, 0.45, 35.5, 34.8, 1, 36.0, 1.76, 3, False, 0.7),
    (1628369, "Jayson Tatum", "BOS", "SF", 51.0, "gtd",     11, 0.31, 0.50, 36.0, 36.4, 1, 35.0, 1.40, 4, False, -0.4),
    (1630162, "Anthony Edwards", "MIN", "SG", 44.5, "healthy", 12, 0.32, 0.62, 36.5, 36.0, 1, 36.0, 1.24, 3, False, 0.5),
    (1628378, "De'Aaron Fox", "SAC", "PG", 41.0, "out",     6,  0.29, 0.65, 0.0,  34.0, 1, 0.0, 1.20, 3, False, 0.0),
    (1630166, "Tyrese Haliburton", "IND", "PG", 42.0, "healthy", 12, 0.27, 0.78, 35.0, 33.5, 1, 35.0, 1.25, 4, False, 1.5),
    (203954,  "Joel Embiid", "PHI", "C", 56.0, "questionable", 8, 0.36, 0.50, 32.0, 33.0, 1, 32.0, 1.69, 3, False, -1.0),
    (1631094, "Victor Wembanyama", "SAS", "C", 46.0, "healthy", 12, 0.30, 0.55, 33.0, 32.0, 1, 33.0, 1.40, 3, False, 1.0),
    # bench/streamer-ish guys
    (1628991, "Aaron Nesmith", "IND", "SF", 22.0, "healthy", 12, 0.16, 0.78, 31.0, 28.0, 2, 32.0, 0.78, 4, False, 3.0),
    (1629677, "Naz Reid", "MIN", "C", 28.0, "healthy", 12, 0.22, 0.62, 27.0, 24.0, 2, 27.0, 1.05, 3, False, 3.0),
    (1630193, "Quentin Grimes", "DAL", "SG", 18.0, "healthy", 12, 0.18, 0.55, 30.0, 22.0, 2, 32.0, 0.65, 4, True, 8.0),  # backup jumping due to injury
    (1631128, "Bilal Coulibaly", "WAS", "SG", 20.0, "healthy", 12, 0.20, 0.58, 30.0, 27.0, 2, 30.0, 0.72, 3, False, 3.0),
    (1641706, "Brandon Miller", "CHA", "SF", 31.0, "healthy", 11, 0.27, 0.50, 33.0, 32.0, 1, 33.0, 1.00, 3, False, 1.0),
    (1629680, "Jalen Williams", "OKC", "SF", 36.0, "healthy", 12, 0.26, 0.58, 33.0, 32.5, 1, 33.0, 1.10, 4, False, 0.5),
    (1631126, "Cason Wallace", "OKC", "SG", 18.0, "healthy", 12, 0.14, 0.58, 26.0, 22.0, 2, 26.0, 0.72, 4, False, 4.0),
    (1629027, "Trae Young", "ATL", "PG", 42.0, "healthy", 12, 0.32, 0.60, 35.0, 35.5, 1, 35.5, 1.20, 3, False, -0.5),
    (1626174, "Domantas Sabonis", "SAC", "C", 47.0, "healthy", 12, 0.27, 0.65, 35.0, 35.0, 1, 36.0, 1.36, 3, True, 1.5),  # Fox out, more usage
    (1641733, "Reed Sheppard", "HOU", "PG", 12.0, "healthy", 10, 0.18, 0.55, 22.0, 18.0, 2, 25.0, 0.62, 4, False, 4.0),
    (1631114, "Scoot Henderson", "POR", "PG", 21.0, "gtd", 9, 0.24, 0.62, 28.0, 27.0, 1, 28.0, 0.78, 3, False, 1.0),
    (1631106, "Jaime Jaquez Jr.", "MIA", "SF", 18.0, "healthy", 12, 0.20, 0.50, 28.0, 24.0, 2, 28.0, 0.72, 4, True, 5.0),  # Butler out
    (1630557, "Walker Kessler", "UTA", "C", 26.0, "healthy", 12, 0.16, 0.58, 28.0, 27.0, 1, 28.0, 0.95, 3, False, 1.0),
    (1629634, "Jeremy Sochan", "SAS", "PF", 24.0, "healthy", 11, 0.20, 0.55, 28.0, 26.0, 2, 28.0, 0.85, 3, False, 2.0),
    (203500,  "Steven Adams", "HOU", "C", 22.0, "healthy", 12, 0.14, 0.55, 23.0, 22.0, 2, 23.0, 0.95, 4, False, 1.0),
    (1641710, "GG Jackson", "MEM", "PF", 19.0, "healthy", 11, 0.22, 0.62, 26.0, 22.0, 2, 27.0, 0.78, 3, True, 4.0),  # Jackson Jr. injury
    (1629639, "Tre Jones", "SAS", "PG", 17.0, "healthy", 12, 0.18, 0.55, 26.0, 22.0, 2, 26.0, 0.72, 3, False, 4.0),
    (1630192, "Jalen Suggs", "ORL", "SG", 28.0, "healthy", 12, 0.21, 0.50, 30.0, 29.0, 1, 30.0, 0.95, 3, False, 1.0),
    (1641760, "Stephon Castle", "SAS", "PG", 22.0, "healthy", 11, 0.20, 0.55, 27.0, 24.0, 2, 28.0, 0.82, 3, True, 3.0),
    (1631110, "Dereck Lively II", "DAL", "C", 24.0, "healthy", 12, 0.16, 0.55, 26.0, 25.0, 1, 26.0, 0.92, 4, False, 1.0),
    (1641723, "Jaylen Wells", "MEM", "SF", 14.0, "healthy", 12, 0.16, 0.62, 27.0, 24.0, 2, 27.0, 0.55, 3, False, 3.0),
    (1641705, "Dalton Knecht", "LAL", "SG", 18.0, "healthy", 12, 0.20, 0.50, 27.0, 22.0, 2, 28.0, 0.72, 3, True, 5.0),  # Vando/Vincent type out
]

OFFLINE_COLUMNS = [
    "id", "name", "team", "position", "fppg_last_season", "status",
    "games_last_30d", "usage_rate", "team_pace_pct", "last10_mpg",
    "season_mpg", "depth_rank", "projected_minutes", "fpts_per_minute",
    "games_this_week", "starter_out", "mpg_delta_last_3",
]


def offline_players() -> list[dict]:
    return [dict(zip(OFFLINE_COLUMNS, row)) for row in OFFLINE_PLAYERS]


def offline_schedule() -> dict:
    return {
        "week_start": "2026-05-18",
        "week_end": "2026-05-24",
        "games_per_team": {
            "ATL": 3, "BOS": 4, "CHA": 3, "DAL": 4, "DEN": 3, "HOU": 4, "IND": 4,
            "LAL": 3, "MEM": 3, "MIA": 4, "MIN": 3, "OKC": 4, "ORL": 3, "PHI": 3,
            "POR": 3, "SAC": 3, "SAS": 3, "UTA": 3, "WAS": 3,
        },
    }


def offline_injuries() -> list[dict]:
    return [
        {"player_id": 1628378, "name": "De'Aaron Fox", "team": "SAC", "status": "out", "expected_return": "2026-05-25", "severity": "high"},
        {"player_id": 203954,  "name": "Joel Embiid",  "team": "PHI", "status": "questionable", "expected_return": None, "severity": "mid"},
        {"player_id": 1628369, "name": "Jayson Tatum", "team": "BOS", "status": "gtd", "expected_return": None, "severity": "low"},
    ]
