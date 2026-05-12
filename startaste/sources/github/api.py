from __future__ import annotations

import logging
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

log = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
RETRY_STRAT = Retry(
    total=5,
    backoff_factor=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)
ADAPTER = HTTPAdapter(max_retries=RETRY_STRAT)


class GithubClient:
    def __init__(self, token: str) -> None:
        http = requests.Session()
        http.mount("https://", ADAPTER)
        http.headers.update({
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3.star+json",
            "X-GitHub-Api-Version": "2022-11-28",
        })
        self._http = http

    def get_starred(self, page: int = 1, per_page: int = 100) -> list[dict]:
        time.sleep(0.2)
        url = f"{GITHUB_API}/user/starred?page={page}&per_page={per_page}"
        log.debug(f"fetching starred repos page {page}")
        resp = self._http.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
