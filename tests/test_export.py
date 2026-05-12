import json

from startaste.sources.hn.models import HnStory, HnComment
from startaste.sources.github.models import GithubStar
from startaste.export import run_export


def _insert_hn_story(id, title="Test Story", time=1700000000):
    HnStory.create(_id=str(id))
    HnStory.save_doc({
        "id": str(id), "type": "story", "by": "alice",
        "time": str(time), "title": title, "url": "https://example.com",
        "score": 42, "descendants": 5,
    })


def _insert_hn_comment(id, text="Test comment", time=1700100000):
    HnComment.create(_id=str(id))
    HnComment.save_doc({
        "id": str(id), "type": "comment", "by": "bob",
        "time": str(time), "parent": "11111", "text": text,
    })


def _insert_github_star(id, name="owner/repo"):
    GithubStar.create(_id=str(id))
    GithubStar.save_doc({
        "starred_at": "2024-06-15T10:30:00Z",
        "repo": {
            "id": id, "full_name": name,
            "description": "A project", "language": "Python",
        },
    })


def test_export_with_data(capsys):
    _insert_hn_story(11111)
    _insert_hn_comment(66666)

    run_export()
    output = json.loads(capsys.readouterr().out)

    assert len(output["hn"]["stories"]) == 1
    assert len(output["hn"]["comments"]) == 1


def test_export_empty_db(capsys):
    run_export()
    output = json.loads(capsys.readouterr().out)

    assert output["hn"]["stories"] == []
    assert output["hn"]["comments"] == []
    assert output["github"]["stars"] == []


def test_export_filter_source(capsys):
    _insert_hn_story(11111)
    _insert_github_star(100001, "alice/project")

    run_export(source="hn")
    output = json.loads(capsys.readouterr().out)

    assert "hn" in output
    assert "github" not in output


def test_export_filter_type(capsys):
    _insert_hn_story(11111)
    _insert_hn_comment(66666)

    run_export(type="story")
    output = json.loads(capsys.readouterr().out)

    assert "stories" in output["hn"]
    assert "comments" not in output["hn"]


def test_export_to_file(tmp_path):
    _insert_hn_story(11111)

    outfile = str(tmp_path / "out.json")
    run_export(file=outfile)

    data = json.loads(open(outfile).read())
    assert len(data["hn"]["stories"]) == 1


def test_export_to_stdout(capsys):
    _insert_hn_story(11111)

    run_export()
    out = capsys.readouterr().out

    data = json.loads(out)
    assert "hn" in data


def test_export_github_stars(capsys):
    _insert_github_star(100001, "alice/project-one")
    _insert_github_star(100002, "bob/project-two")

    run_export(source="github")
    output = json.loads(capsys.readouterr().out)

    assert len(output["github"]["stars"]) == 2
