#!/usr/bin/env python
"""Python-Pinboard

Python script for downloading your saved stories and saved comments on Hacker News
and converting them to a JSON format for easy use.

Originally written on Pythonista on iPad
"""


from __future__ import annotations
import pathlib

__version__ = (pathlib.Path(__file__).parent / "VERSION").read_text().strip()
__license__ = "BSD"
__copyright__ = "Copyright 2013-2014, Luciano Fiandesio"
__author__ = "Luciano Fiandesio <http://fiandes.io/> & John David Pressman <http://jdpressman.com> & Kraktus"

import argparse
import time
import re
import sys
import json
import os
import logging
import logging.handlers
import requests
from peewee import SqliteDatabase, Model, CharField, DateTimeField, IntegrityError

from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

#############
# Constants #
#############

load_dotenv()

LOG_PATH = f"{__file__}.log"
HACKERNEWS = "https://news.ycombinator.com"
HEADERS = {  # we need to specify an header to get the right cookie
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


def get_env(name: str):
    return os.getenv(f"HN_COMMENTS_{name.upper()}")


USERNAME = get_env("acct")
PASSWORD = get_env("pw")

assert USERNAME is not None, "username is required, in .env set HN_COMMENTS_ACCT"
assert PASSWORD is not None, "password is required, in .env set HN_COMMENTS_PW"

DATABASE = "hn.db"

########
# Logs #
########

log = logging.getLogger(__file__)
log.setLevel(logging.DEBUG)
format_string = "%(asctime)s | %(levelname)-8s | %(message)s"

# 125000000 bytes = 12.5Mb
handler = logging.handlers.RotatingFileHandler(
    LOG_PATH, maxBytes=12500000, backupCount=3, encoding="utf8"
)
handler.setFormatter(logging.Formatter(format_string))
handler.setLevel(logging.DEBUG)
log.addHandler(handler)

handler_2 = logging.StreamHandler(sys.stdout)
handler_2.setFormatter(logging.Formatter("%(message)s"))

###########
# Classes #
###########

# create a peewee database instance -- our models will use this database to
# persist information
database = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = database


# a HN doc, either story or comment
class Doc(BaseModel):
    _id = CharField(unique=True)
    body = CharField(null=True)  # TODO use JSONField playhouse extension
    timestamp = DateTimeField(null=True)

    @classmethod
    def list_empty(cls) -> list[Doc]:
        return cls.select(cls._id).where(cls.body.is_null(True))

    @classmethod
    def save_ids(cls, ids: list[str]):
        # "slow" but otherwise how to silently disregard ids already in place?
        for _id in ids:
            try:
                user = cls.create(_id=_id)
            except IntegrityError as e:
                pass  # story already in the db

    @classmethod
    def count_empty(cls) -> int:
        return cls.list_empty().count()  # type: ignore

    @classmethod
    def to_dict(cls) -> list[dict[str, str]]:
        return [
            json.loads(x["body"])
            for x in cls.select(cls.body)
            .where(cls.body.is_null(False))
            .order_by(cls.timestamp.desc())
            .dicts()
        ]

    @classmethod
    def save_doc(cls, doc: dict[str, str]):
        timestamp = datetime.fromtimestamp(int(doc["time"]))
        cls.update(body=json.dumps(doc), timestamp=timestamp).where(
            cls._id == doc["id"]
        ).execute()


class Story(Doc):
    pass


class Comment(Doc):
    pass


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

    def login(self) -> None:
        # Build the login POST data and make the login request.
        payload = {"whence": "news", "acct": USERNAME, "pw": PASSWORD}
        auth = self.post(f"{HACKERNEWS}/login", data=payload)
        if "Bad login" in str(auth.content) or auth.status_code != 200:
            raise Exception("Hacker News authentication failed!")
        if USERNAME is not None and USERNAME not in str(auth.content):
            raise Exception("Hacker News didn't succeed, username not displayed.")

    def _get_hn_doc(self, user, comments: bool, klass: str, max_page: int) -> list[str]:
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
                break  # we reached last page
            else:
                ids.extend(page_ids)
        return ids

    def get_upvoted_stories(self, max_page: int) -> list[str]:
        """Return a list of story IDs representing your saved stories.
        This function does not return the actual metadata associated, just the IDs.
        This list is traversed and each item inside is grabbed using the Hacker News
        API by story ID."""
        return self._get_hn_doc(
            user=USERNAME, comments=False, klass="subtext", max_page=max_page
        )

    def get_upvoted_comments(self, max_page: int) -> list[str]:
        """Return a list of IDs representing your saved comments.
        This function does not return the actual metadata associated, just the IDs.
        This list is traversed and each item inside is grabbed using the Hacker News
        API by ID."""
        return self._get_hn_doc(
            user=USERNAME, comments=True, klass="default", max_page=max_page
        )

    def get_item(self, item_id):
        """Get an 'item' as specified in the HackerNews v0 API."""
        time.sleep(0.2)
        item_json_link = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
        return self.get(item_json_link).json()


def log_item(item_id, item_count, item_total):
    log.info(f"Got item  {item_id} ({item_count} of {item_total})")


def create_tables():
    with database:
        database.create_tables([Story, Comment])


def main():
    create_tables()
    database.connect()
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Filepath to store the JSON document at.")
    parser.add_argument(
        "-n",
        "--number",
        default=1,
        type=int,
        help="Number of pages to grab, default 1.",
    )
    # add argument to parse, list whether they want stories, comments, or both
    parser.add_argument(
        "-s",
        "--select",
        nargs="+",
        choices=["story", "comment"],
        help="select which items to grab",
        default=["story", "comment"],
    )
    # log level, default debug
    parser.add_argument(
        "-l",
        "--log",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="set log level",
        default="INFO",
    )

    arguments = parser.parse_args()
    handler_2.setLevel(arguments.log)
    log.addHandler(handler_2)

    json_items = {"saved_stories": list(), "saved_comments": list()}
    item_count = 0
    req = Req()
    req.login()
    max_page = arguments.number + 1
    if "story" in arguments.select:
        all_story_ids = req.get_upvoted_stories(max_page)
        Story.save_ids(all_story_ids)
        query_empty = Story.list_empty()
        count_empty = Story.count_empty()
        log.debug(f"story_ids {query_empty}")
        for story in query_empty:
            Story.save_doc(req.get_item(story._id))
            item_count += 1
            log_item(story._id, item_count, count_empty)
        json_items["saved_stories"] = Story.to_dict()
    if "comment" in arguments.select:
        all_comment_ids = req.get_upvoted_comments(max_page)
        Comment.save_ids(all_comment_ids)
        query_empty = Comment.list_empty()
        count_empty = Comment.count_empty()
        log.debug(f"comment_ids {query_empty}")
        for comment in query_empty:
            Comment.save_doc(req.get_item(comment._id))
            item_count += 1
            log_item(comment._id, item_count, count_empty)
        json_items["saved_comments"] = Comment.to_dict()
    if arguments.file:
        with open(arguments.file, "w") as outfile:
            json.dump(json_items, outfile, indent=2)
    else:
        print(json.dumps(json_items, indent=2))
    database.close()


if __name__ == "__main__":
    main()
