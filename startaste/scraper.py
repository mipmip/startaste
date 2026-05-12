from __future__ import annotations

import logging
import os
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

load_dotenv()

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


def get_credentials() -> tuple[str, str]:
    username = os.getenv("HN_COMMENTS_ACCT")
    password = os.getenv("HN_COMMENTS_PW")
    if not username:
        raise SystemExit("Error: HN_COMMENTS_ACCT not set in environment or .env")
    if not password:
        raise SystemExit("Error: HN_COMMENTS_PW not set in environment or .env")
    return username, password


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

    def login(self, username: str, password: str) -> None:
        payload = {"whence": "news", "acct": username, "pw": password}
        auth = self.post(f"{HACKERNEWS}/login", data=payload)
        if "Bad login" in str(auth.content) or auth.status_code != 200:
            raise Exception("Hacker News authentication failed!")
        if username not in str(auth.content):
            raise Exception("Hacker News didn't succeed, username not displayed.")

    def scrape_ids(self, user: str, comments: bool, klass: str, max_page: int) -> list[str]:
        ids = []
        for page in range(1, max_page):
            time.sleep(0.5)
            log.debug(f"saving {'comments' if comments else 'stories'} page {page}")
            saved = self.get(
                f"{HACKERNEWS}/upvoted?id={user}{'&comments=t' if comments else ''}&p={page}"
            )
            soup = BeautifulSoup(saved.content, features="html.parser")
            page_ids = []
            for tag in soup.find_all("td", attrs={"class": klass}):
                if tag.a is not type(None):
                    a_tags = tag.find_all("a")
                    for a_tag in a_tags:
                        if a_tag["href"][:5] == "item?":
                            story_id = a_tag["href"].split("id=")[1]
                            page_ids.append(story_id)
                            break
            if len(page_ids) == 0:
                log.debug(f"BREAK {saved.content}")
                break
            else:
                ids.extend(page_ids)
        return ids

    def get_upvoted_stories(self, user: str, max_page: int) -> list[str]:
        return self.scrape_ids(user=user, comments=False, klass="subtext", max_page=max_page)

    def get_upvoted_comments(self, user: str, max_page: int) -> list[str]:
        return self.scrape_ids(user=user, comments=True, klass="default", max_page=max_page)

    def get_item(self, item_id: str) -> dict:
        time.sleep(0.2)
        item_json_link = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
        return self.get(item_json_link).json()
