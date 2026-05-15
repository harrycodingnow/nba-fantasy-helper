"""Quick sanity tests for the engines. Run: python -m ingestion.test_engines"""
from ingestion import engines, sample_data


def test_fantasy_points():
    row = {"PTS": 25, "REB": 8, "AST": 7, "STL": 1, "BLK": 1, "TOV": 3, "FG3M": 2}
    fp = engines.fantasy_points(row)
    # 25 + 8 + 14 + 4 + 4 - 6 + 2 = 51
    assert fp == 51, fp


def test_injury_factor_bands():
    out, _ = engines.injury_risk_factor("out", 0)
    assert out == 0.50
    healthy, _ = engines.injury_risk_factor("healthy", 12)
    assert 1.0 < healthy <= 1.05
    gtd, _ = engines.injury_risk_factor("gtd", 12)
    assert 0.7 < gtd < 0.85


def test_opportunity_factor_clamped():
    assert engines.opportunity_factor(0.40, 1.0) <= 1.30
    assert engines.opportunity_factor(0.10, 0.0) >= 0.85


def test_roster_factor():
    assert engines.roster_factor(1) == 1.15
    assert engines.roster_factor(2) == 1.00
    assert engines.roster_factor(99) == 0.90


def test_compute_player_value_shape():
    p = sample_data.offline_players()[0]  # Luka
    pv = engines.compute_player_value(p)
    assert pv.dynamic_value > 0
    assert pv.breakdown["multipliers"]["injury_risk_factor"] == pv.injury_risk_factor


def test_compute_opportunity_starter_out_boost():
    # Quentin Grimes — starter_out=True, depth_rank=2 → boost ≥ 1.35 (× minutes-up boost)
    qg = next(x for x in sample_data.offline_players() if x["name"] == "Quentin Grimes")
    op = engines.compute_opportunity(qg)
    assert op.opportunity_boost >= 1.35
    assert "starter out" in op.why


def test_compute_opportunity_stable_role():
    luka = next(x for x in sample_data.offline_players() if x["name"] == "Luka Doncic")
    op = engines.compute_opportunity(luka)
    assert op.opportunity_boost == 1.0


if __name__ == "__main__":
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  ok  {t.__name__}")
        except AssertionError as e:
            print(f"  FAIL {t.__name__}: {e}")
            failed += 1
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    raise SystemExit(failed)
