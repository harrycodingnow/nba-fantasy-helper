"""Points-league fantasy scoring + engine math.

All multipliers are intentionally interpretable. The UI shows the breakdown
to the user; if a number looks wrong, the multiplier values explain why.

Points-league formula (ESPN standard):
    pts*1 + reb*1 + ast*2 + stl*4 + blk*4 + tov*-2 + 3pm*1
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional

# ----------------------------- scoring --------------------------------------

POINTS_WEIGHTS = {
    "PTS": 1.0,
    "REB": 1.0,
    "AST": 2.0,
    "STL": 4.0,
    "BLK": 4.0,
    "TOV": -2.0,
    "FG3M": 1.0,
}


def fantasy_points(stat_row: dict) -> float:
    """Compute points-league fantasy points from a per-game stat row."""
    return sum(stat_row.get(k, 0) * w for k, w in POINTS_WEIGHTS.items())


# ----------------------------- multipliers ----------------------------------


def injury_risk_factor(status: str, games_last_30d: int) -> tuple[float, str]:
    """Lower = more risky.

    status: 'healthy' | 'gtd' (game-time-decision) | 'out' | 'questionable'
    """
    s = (status or "healthy").lower()
    if s == "out":
        return 0.50, "Out — ignore unless waiver stash"
    if s in ("gtd", "questionable"):
        base = 0.80
    else:
        base = 1.05  # tiny premium for fully healthy

    # additionally penalize chronic absences
    if games_last_30d <= 4:
        base *= 0.85
    elif games_last_30d <= 7:
        base *= 0.95

    return round(base, 3), {
        0.50: "high",
        0.80: "mid",
    }.get(round(base, 2), "low")[0:3] + " risk"


def opportunity_factor(usage_rate: float, team_pace_pct: float) -> float:
    """usage_rate in [0, 0.5], team_pace_pct in [0,1] (percentile vs league)."""
    usage = max(0.10, min(usage_rate, 0.40))
    pace = max(0.0, min(team_pace_pct, 1.0))
    # base 1.0 at usage=0.20 (avg) and pace=0.5
    val = 1.0 + (usage - 0.20) * 1.5 + (pace - 0.5) * 0.20
    return round(max(0.85, min(val, 1.30)), 3)


def minutes_factor(last10_mpg: float, season_mpg: float) -> float:
    """Trend: are minutes rising vs season baseline?"""
    if season_mpg <= 0:
        return 1.0
    ratio = last10_mpg / season_mpg
    val = 0.85 + (ratio - 0.95) * 1.0
    return round(max(0.7, min(val, 1.20)), 3)


def roster_factor(depth_rank: int) -> float:
    """depth_rank: 1=starter, 2=primary backup, 3+=deep bench."""
    return {1: 1.15, 2: 1.00, 3: 0.95}.get(depth_rank, 0.90)


def risk_label(base_value: float, injury_mult: float, opportunity_mult: float) -> str:
    tier = (
        "Superstar" if base_value >= 45
        else "Star" if base_value >= 35
        else "Starter" if base_value >= 25
        else "Role player" if base_value >= 15
        else "Deep bench"
    )
    risk = (
        "High Risk" if injury_mult <= 0.65
        else "Mid Risk" if injury_mult <= 0.85
        else "Low Risk"
    )
    upside = "" if opportunity_mult < 1.10 else " · Rising"
    return f"{risk} {tier}{upside}"


# ----------------------------- engines --------------------------------------


@dataclass
class PlayerValue:
    player_id: int
    name: str
    team: str
    position: str
    base_value: float
    injury_risk_factor: float
    opportunity_factor: float
    minutes_factor: float
    roster_factor: float
    dynamic_value: float
    risk_label: str
    breakdown: dict = field(default_factory=dict)


def compute_player_value(player: dict) -> PlayerValue:
    """player keys: id, name, team, position, fppg_last_season, status,
    games_last_30d, usage_rate, team_pace_pct, last10_mpg, season_mpg, depth_rank."""
    base = float(player.get("fppg_last_season", 0.0))
    inj, _inj_short = injury_risk_factor(player.get("status", "healthy"), int(player.get("games_last_30d", 30)))
    opp = opportunity_factor(float(player.get("usage_rate", 0.20)), float(player.get("team_pace_pct", 0.5)))
    mins = minutes_factor(float(player.get("last10_mpg", player.get("season_mpg", 0.0))), float(player.get("season_mpg", 0.0)))
    rost = roster_factor(int(player.get("depth_rank", 2)))
    dyn = round(base * inj * opp * mins * rost, 2)
    label = risk_label(base, inj, opp)

    return PlayerValue(
        player_id=int(player["id"]),
        name=player["name"],
        team=player.get("team", ""),
        position=player.get("position", ""),
        base_value=round(base, 2),
        injury_risk_factor=inj,
        opportunity_factor=opp,
        minutes_factor=mins,
        roster_factor=rost,
        dynamic_value=dyn,
        risk_label=label,
        breakdown={
            "formula": "base × injury × opportunity × minutes × roster",
            "inputs": {
                "fppg_last_season": base,
                "status": player.get("status", "healthy"),
                "games_last_30d": int(player.get("games_last_30d", 30)),
                "usage_rate": float(player.get("usage_rate", 0.20)),
                "team_pace_pct": float(player.get("team_pace_pct", 0.5)),
                "last10_mpg": float(player.get("last10_mpg", 0.0)),
                "season_mpg": float(player.get("season_mpg", 0.0)),
                "depth_rank": int(player.get("depth_rank", 2)),
            },
            "multipliers": {
                "injury_risk_factor": inj,
                "opportunity_factor": opp,
                "minutes_factor": mins,
                "roster_factor": rost,
            },
        },
    )


# -------- Opportunity (weekly streamer) engine ------------------------------


@dataclass
class OpportunityPick:
    player_id: int
    name: str
    team: str
    position: str
    projected_minutes: float
    fpts_per_minute: float
    games_this_week: int
    opportunity_boost: float
    weekly_value: float
    why: str


def opportunity_boost(starter_out: bool, depth_rank: int, mpg_delta_last_3: float) -> tuple[float, str]:
    """Detect lineup shift opportunities.

    starter_out: True if a teammate ahead of them on the depth chart is OUT.
    depth_rank: this player's depth chart slot.
    mpg_delta_last_3: change in minutes over last 3 games vs season baseline.
    """
    boost = 1.0
    reasons: list[str] = []
    if starter_out and depth_rank in (2, 3):
        boost *= 1.35
        reasons.append("starter out → promoted into rotation")
    if mpg_delta_last_3 >= 6:
        boost *= 1.15
        reasons.append(f"minutes up {mpg_delta_last_3:+.0f} vs baseline")
    elif mpg_delta_last_3 <= -6:
        boost *= 0.85
        reasons.append(f"minutes down {mpg_delta_last_3:+.0f}")
    why = "; ".join(reasons) if reasons else "stable role"
    return round(boost, 3), why


def compute_opportunity(player: dict) -> OpportunityPick:
    """player keys (in addition to compute_player_value's): projected_minutes,
    fpts_per_minute, games_this_week, starter_out, mpg_delta_last_3."""
    boost, why = opportunity_boost(
        bool(player.get("starter_out", False)),
        int(player.get("depth_rank", 2)),
        float(player.get("mpg_delta_last_3", 0.0)),
    )
    proj_min = float(player.get("projected_minutes", player.get("season_mpg", 0.0)))
    fpm = float(player.get("fpts_per_minute", 0.0))
    games = int(player.get("games_this_week", 3))
    weekly = round(proj_min * fpm * games * boost, 2)

    games_blurb = f"{games}-game week"
    full_why = f"{games_blurb}; {why}"

    return OpportunityPick(
        player_id=int(player["id"]),
        name=player["name"],
        team=player.get("team", ""),
        position=player.get("position", ""),
        projected_minutes=round(proj_min, 1),
        fpts_per_minute=round(fpm, 3),
        games_this_week=games,
        opportunity_boost=boost,
        weekly_value=weekly,
        why=full_why,
    )


# ---- helpers used by UI -----------------------------------------------------

def player_value_to_dict(pv: PlayerValue) -> dict:
    return asdict(pv)


def opportunity_to_dict(op: OpportunityPick) -> dict:
    return asdict(op)
