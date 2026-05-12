import json

from datetime import datetime

from startaste.db import Doc


class GithubStar(Doc):
    class Meta:
        table_name = "github_star"

    @classmethod
    def save_doc(cls, doc: dict):
        starred_at = doc.get("starred_at", "")
        if starred_at:
            timestamp = datetime.fromisoformat(starred_at.replace("Z", "+00:00"))
        else:
            timestamp = datetime.now()
        repo = doc.get("repo", {})
        repo_id = str(repo.get("id", doc.get("id", "")))
        cls.update(body=json.dumps(doc), timestamp=timestamp).where(
            cls._id == repo_id
        ).execute()
