"""NBA Stats API client.

Talks to stats.nba.com via the swar/nba_api package's HTTP layer so we inherit
their maintained headers (stats.nba.com rotates anti-bot defenses; rolling our
own User-Agent gets us 403/timeouts within months). Same on-disk JSON cache
keyed by (endpoint, date) so we don't hammer them during dev.
"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import date
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlencode

from nba_api.stats.library.http import NBAStatsHTTP

CACHE_DIR = Path(__file__).resolve().parent / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

REQUEST_DELAY_SEC = 0.6  # rate-limit polite floor
REQUEST_TIMEOUT_SEC = 30

_HTTP = NBAStatsHTTP()


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

    time.sleep(REQUEST_DELAY_SEC)
    resp = _HTTP.send_api_request(endpoint=endpoint, parameters=params, timeout=REQUEST_TIMEOUT_SEC)
    data = resp.get_dict()
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
