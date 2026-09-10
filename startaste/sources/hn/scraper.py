from __future__ import annotations

import logging
import os
import time

from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from startaste.sources.base import SourceAuthError, SourceUnavailableError

log = logging.getLogger(__name__)

HACKERNEWS = "https://news.ycombinator.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
RETRY_STRAT = Retry(
    total=5,
    backoff_factor=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)
ADAPTER = HTTPAdapter(max_retries=RETRY_STRAT)
MAX_PAGES = 200


def get_credentials() -> tuple[str, str]:
    username = os.getenv("HN_COMMENTS_ACCT")
    password = os.getenv("HN_COMMENTS_PW")
    if not username:
        raise SystemExit("Error: HN_COMMENTS_ACCT not set in environment or .env")
    if not password:
        raise SystemExit("Error: HN_COMMENTS_PW not set in environment or .env")
    return username, password


def extract_ids(soup: BeautifulSoup, klass: str) -> list[str]:
    ids = []
    for tag in soup.find_all("td", attrs={"class": klass}):
        for a_tag in tag.find_all("a"):
            href = a_tag.get("href", "")
            if href.startswith("item?"):
                ids.append(href.split("id=")[1])
                break
    return ids


def next_page_url(soup: BeautifulSoup) -> str | None:
    # HN paginates /upvoted with a cursor in the More link (next/n/time), not
    # with a p= parameter — p= is ignored there and always returns page one.
    more = soup.find("a", class_="morelink") or soup.find("a", rel="next")
    if not more or not more.get("href"):
        return None
    return urljoin(f"{HACKERNEWS}/", more["href"])


class Req:
    def __init__(self) -> None:
        http = requests.Session()
        http.mount("https://", ADAPTER)
        http.mount("http://", ADAPTER)
        self._http = http

    def get(self, url: str) -> requests.Response:
        return self._http.get(url, headers=HEADERS, timeout=30)

    def post(self, url: str, data: dict[str, str]) -> requests.Response:
        return self._http.post(url, data=data, headers=HEADERS, timeout=30)

    HN_ENV_VARS = ["HN_COMMENTS_ACCT", "HN_COMMENTS_PW"]

    def login(self, username: str, password: str) -> None:
        payload = {"whence": "news", "acct": username, "pw": password}
        try:
            auth = self.post(f"{HACKERNEWS}/login", data=payload)
        except requests.RequestException as exc:
            raise SourceUnavailableError(
                "hn", f"could not reach Hacker News to log in ({type(exc).__name__})"
            ) from None

        if "Bad login" in str(auth.content) or auth.status_code != 200:
            raise SourceAuthError(
                "hn",
                "Hacker News refused the account and password",
                self.HN_ENV_VARS,
            ) from None
        if username not in str(auth.content):
            raise SourceAuthError(
                "hn",
                f"logged in but Hacker News did not show {username} as signed in",
                self.HN_ENV_VARS,
            ) from None

    def iter_upvoted(
        self, user: str, comments: bool, klass: str, max_page: int = MAX_PAGES
    ):
        """Yield the item IDs of each page of an upvoted listing, in order."""
        label = "comments" if comments else "stories"
        url = f"{HACKERNEWS}/upvoted?id={user}{'&comments=t' if comments else ''}"
        collected = 0

        for page in range(1, max_page + 1):
            time.sleep(0.5)
            log.debug(f"scraping upvoted {label} page {page}")
            saved = self.get(url)
            soup = BeautifulSoup(saved.content, features="html.parser")

            page_ids = extract_ids(soup, klass)
            if not page_ids:
                return

            collected += len(page_ids)
            yield page_ids

            url = next_page_url(soup)
            if url is None:
                log.debug(f"no More link after {label} page {page}, listing complete")
                return

        log.warning(
            f"stopped scraping upvoted {label} at the {max_page} page limit "
            f"with {collected} IDs collected; the listing may be longer"
        )

    def scrape_ids(self, user: str, comments: bool, klass: str, max_page: int = MAX_PAGES) -> list[str]:
        ids = []
        for page_ids in self.iter_upvoted(user, comments, klass, max_page):
            ids.extend(page_ids)
        return ids

    def get_upvoted_stories(self, user: str, max_page: int = MAX_PAGES) -> list[str]:
        return self.scrape_ids(user=user, comments=False, klass="subtext", max_page=max_page)

    def get_upvoted_comments(self, user: str, max_page: int = MAX_PAGES) -> list[str]:
        return self.scrape_ids(user=user, comments=True, klass="default", max_page=max_page)

    def get_item(self, item_id: str) -> dict:
        time.sleep(0.2)
        item_json_link = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
        return self.get(item_json_link).json()
