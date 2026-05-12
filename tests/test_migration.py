from peewee import SqliteDatabase, CharField, Model, DateTimeField

from startaste.db import database, migrate_tables
from startaste.sources.hn.models import HnStory, HnComment


def test_migrates_old_tables():
    # Drop new-style tables so only old ones exist
    database.execute_sql('DROP TABLE IF EXISTS "hn_story"')
    database.execute_sql('DROP TABLE IF EXISTS "hn_comment"')
    # Create old-style tables
    database.execute_sql('CREATE TABLE "story" ("_id" VARCHAR(255) UNIQUE, "body" VARCHAR(255), "timestamp" DATETIME)')
    database.execute_sql('CREATE TABLE "comment" ("_id" VARCHAR(255) UNIQUE, "body" VARCHAR(255), "timestamp" DATETIME)')
    database.execute_sql('INSERT INTO "story" ("_id", "body") VALUES (?, ?)', ["11111", '{"id": "11111"}'])

    migrate_tables()

    tables = database.get_tables()
    assert "hn_story" in tables
    assert "hn_comment" in tables
    assert "story" not in tables
    assert "comment" not in tables

    # Data preserved
    assert HnStory.count_all() == 1


def test_already_migrated():
    # Tables already have new names (from conftest fixture)
    migrate_tables()
    tables = database.get_tables()
    assert "hn_story" in tables


def test_fresh_database():
    # Drop all tables to simulate fresh
    database.drop_tables([HnStory, HnComment])
    tables = database.get_tables()
    assert "hn_story" not in tables
    assert "story" not in tables

    # Migration does nothing, create_tables makes them
    migrate_tables()
    database.create_tables([HnStory, HnComment])
    tables = database.get_tables()
    assert "hn_story" in tables
