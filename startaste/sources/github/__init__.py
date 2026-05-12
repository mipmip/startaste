from __future__ import annotations

import logging
import os

from startaste.sources.base import Source
from startaste.sources.github.models import GithubStar
from startaste.sources.github.api import GithubClient

log = logging.getLogger(__name__)


class GithubSource(Source):
    name = "github"
    item_types = ["star"]
    models = [GithubStar]
    env_help = {
        "GITHUB_TOKEN": "GitHub personal access token (github.com/settings/tokens)",
    }

    def is_configured(self) -> bool:
        return bool(os.getenv("GITHUB_TOKEN"))

    def sync(self) -> None:
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise SystemExit("Error: GITHUB_TOKEN not set in environment or .env")

        client = GithubClient(token)
        is_full = GithubStar.count_all() == 0

        if is_full:
            log.info("GitHub full sync: fetching all starred repos")
        else:
            log.info("GitHub incremental sync: stopping when all repos on a page are known")

        all_ids = []
        page = 1

        while True:
            stars = client.get_starred(page=page)

            if not stars:
                break

            page_ids = []
            for star in stars:
                repo = star.get("repo", {})
                repo_id = str(repo.get("id", ""))
                page_ids.append(repo_id)

            if not is_full:
                all_known = all(GithubStar.has_id(_id) for _id in page_ids)
                if all_known:
                    log.debug(f"incremental: all repos on page {page} are known, stopping")
                    all_ids.extend(page_ids)
                    break

            all_ids.extend(page_ids)
            page += 1

        GithubStar.save_ids(all_ids)

        # Fetch metadata — for GitHub, we already have it from the starred API
        # Re-save with full body for items that are empty
        page = 1
        empty_count = GithubStar.count_empty()
        if empty_count > 0:
            log.info(f"Storing metadata for {empty_count} stars")
            fetched = 0
            while True:
                stars = client.get_starred(page=page)
                if not stars:
                    break
                for star in stars:
                    repo = star.get("repo", {})
                    repo_id = str(repo.get("id", ""))
                    if GithubStar.has_id(repo_id):
                        empty = GithubStar.select().where(
                            (GithubStar._id == repo_id) & (GithubStar.body.is_null(True))
                        ).exists()
                        if empty:
                            GithubStar.save_doc(star)
                            fetched += 1
                            log.info(f"Got star {repo.get('full_name', repo_id)} ({fetched} of {empty_count})")
                if fetched >= empty_count:
                    break
                page += 1

        log.info("GitHub sync complete")
