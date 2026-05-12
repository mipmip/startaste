from __future__ import annotations

import json
import logging

from datetime import datetime
from peewee import SqliteDatabase, Model, CharField, DateTimeField, IntegrityError

log = logging.getLogger(__name__)

database = SqliteDatabase(None)


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


def init_database():
    from startaste.paths import get_db_path, ensure_dirs, migrate_db_file
    ensure_dirs()
    migrate_db_file()
    db_path = str(get_db_path())
    database.init(db_path)
    database.connect(reuse_if_open=True)
    migrate_tables()
    database.create_tables(_get_all_models())


def migrate_tables():
    tables = database.get_tables()
    renames = {"story": "hn_story", "comment": "hn_comment"}
    for old, new in renames.items():
        if old in tables and new not in tables:
            log.info(f"Migrating table: {old} → {new}")
            database.execute_sql(f'ALTER TABLE "{old}" RENAME TO "{new}"')


def _get_all_models():
    from startaste.sources import get_sources
    models = []
    for source in get_sources():
        models.extend(source.models)
    return models


def create_tables():
    migrate_tables()
    database.create_tables(_get_all_models())
