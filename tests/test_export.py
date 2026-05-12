import json

from startaste.db import Story, Comment
from startaste.export import run_export


def _insert_story(id, title="Test Story", time=1700000000):
    Story.create(_id=str(id))
    Story.save_doc({
        "id": str(id), "type": "story", "by": "alice",
        "time": str(time), "title": title, "url": "https://example.com",
        "score": 42, "descendants": 5,
    })


def _insert_comment(id, text="Test comment", time=1700100000):
    Comment.create(_id=str(id))
    Comment.save_doc({
        "id": str(id), "type": "comment", "by": "bob",
        "time": str(time), "parent": "11111", "text": text,
    })


def test_export_with_data(capsys):
    _insert_story(11111)
    _insert_comment(66666)

    run_export()
    output = json.loads(capsys.readouterr().out)

    assert len(output["saved_stories"]) == 1
    assert len(output["saved_comments"]) == 1
    assert output["saved_stories"][0]["id"] == "11111"
    assert output["saved_comments"][0]["id"] == "66666"


def test_export_empty_db(capsys):
    run_export()
    output = json.loads(capsys.readouterr().out)

    assert output["saved_stories"] == []
    assert output["saved_comments"] == []


def test_export_filter_story(capsys):
    _insert_story(11111)
    _insert_comment(66666)

    run_export(select=["story"])
    output = json.loads(capsys.readouterr().out)

    assert len(output["saved_stories"]) == 1
    assert output["saved_comments"] == []


def test_export_filter_comment(capsys):
    _insert_story(11111)
    _insert_comment(66666)

    run_export(select=["comment"])
    output = json.loads(capsys.readouterr().out)

    assert output["saved_stories"] == []
    assert len(output["saved_comments"]) == 1


def test_export_to_file(tmp_path):
    _insert_story(11111)

    outfile = str(tmp_path / "out.json")
    run_export(file=outfile)

    data = json.loads(open(outfile).read())
    assert len(data["saved_stories"]) == 1


def test_export_to_stdout(capsys):
    _insert_story(11111)

    run_export()
    out = capsys.readouterr().out

    data = json.loads(out)
    assert "saved_stories" in data
    assert "saved_comments" in data
