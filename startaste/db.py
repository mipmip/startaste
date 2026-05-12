from __future__ import annotations

import json
import os

from datetime import datetime
from peewee import SqliteDatabase, Model, CharField, DateTimeField, IntegrityError

DATABASE = os.environ.get("STARTASTE_DB", "hn.db")

database = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = database


class Doc(BaseModel):
    _id = CharField(unique=True)
    body = CharField(null=True)
    timestamp = DateTimeField(null=True)

    @classmethod
    def list_empty(cls) -> list[Doc]:
        return cls.select(cls._id).where(cls.body.is_null(True))

    @classmethod
    def save_ids(cls, ids: list[str]):
        for _id in ids:
            try:
                cls.create(_id=_id)
            except IntegrityError:
                pass

    @classmethod
    def count_empty(cls) -> int:
        return cls.list_empty().count()  # type: ignore

    @classmethod
    def count_all(cls) -> int:
        return cls.select().count()  # type: ignore

    @classmethod
    def has_id(cls, _id: str) -> bool:
        return cls.select().where(cls._id == _id).exists()

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


def create_tables():
    with database:
        database.create_tables([Story, Comment])
