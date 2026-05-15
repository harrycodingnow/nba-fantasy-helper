"""NBA Stats API client.

Talks to stats.nba.com unofficial endpoints. Requires browser-like headers or
the API returns 403. Caches raw JSON responses keyed by (endpoint, date) so we
don't hammer them during dev.
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import date
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlencode

import requests

CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

BASE_URL = "https://stats.nba.com/stats"

# stats.nba.com is allergic to non-browser User-Agents.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.0 Safari/605.1.15"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.nba.com",
    "Referer": "https://www.nba.com/",
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
}

REQUEST_DELAY_SEC = 0.6  # rate-limit polite floor


def _cache_path(endpoint: str, params: dict[str, Any]) -> Path:
    key = endpoint + "?" + urlencode(sorted(params.items()))
    digest = hashlib.sha1(key.encode()).hexdigest()[:16]
    today = date.today().isoformat()
    return CACHE_DIR / f"{today}_{endpoint}_{digest}.json"


def fetch(endpoint: str, params: Optional[dict[str, Any]] = None, *, force: bool = False) -> dict:
    params = params or {}
    cache_file = _cache_path(endpoint, params)
    if cache_file.exists() and not force:
        return json.loads(cache_file.read_text())

    url = f"{BASE_URL}/{endpoint}"
    time.sleep(REQUEST_DELAY_SEC)
    resp = requests.get(url, params=params, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    cache_file.write_text(json.dumps(data))
    return data


def rows_from_resultset(payload: dict, set_name: Optional[str] = None) -> list[dict]:
    """NBA Stats returns {resultSets: [{name, headers, rowSet}]}. Flatten to dicts."""
    sets = payload.get("resultSets") or payload.get("resultSet")
    if isinstance(sets, dict):
        sets = [sets]
    for rs in sets:
        if set_name and rs.get("name") != set_name:
            continue
        headers = rs["headers"]
        return [dict(zip(headers, row)) for row in rs["rowSet"]]
    return []
