from __future__ import annotations

import logging
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from startaste.sources.base import SourceAuthError, SourceUnavailableError

log = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
RETRY_STRAT = Retry(
    total=5,
    backoff_factor=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)
ADAPTER = HTTPAdapter(max_retries=RETRY_STRAT)


def _rejection(resp: requests.Response) -> SourceAuthError | SourceUnavailableError:
    """Tell a rejected token apart from an exhausted rate limit.

    GitHub answers 403 for both, so the status alone is not enough: a rate-limit
    refusal carries a remaining count of zero.
    """
    if resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0":
        reset = resp.headers.get("X-RateLimit-Reset", "unknown")
        return SourceUnavailableError(
            "github", f"GitHub rate limit exhausted (resets at {reset}); try again later"
        )
    return SourceAuthError(
        "github",
        f"GITHUB_TOKEN was rejected ({resp.status_code}). Renew it at "
        "github.com/settings/tokens",
        ["GITHUB_TOKEN"],
    )


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
        try:
            resp = self._http.get(url, timeout=30)
        except requests.RequestException as exc:
            # Includes retry exhaustion: the adapter already retries 429 and 5xx.
            raise SourceUnavailableError(
                "github", f"could not reach the GitHub API ({type(exc).__name__})"
            ) from None

        if resp.status_code in (401, 403):
            raise _rejection(resp) from None

        try:
            resp.raise_for_status()
        except requests.HTTPError:
            raise SourceUnavailableError(
                "github", f"the GitHub API returned {resp.status_code}"
            ) from None

        return resp.json()
