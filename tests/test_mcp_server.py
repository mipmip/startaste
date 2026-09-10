import asyncio
import json

import pytest
from starlette.testclient import TestClient

from startaste.mcp.auth import hash_token
from startaste.mcp.server import build_app, build_mcp
from startaste.sources.github.models import GithubStar
from startaste.sources.hn.models import HnStory

TOOLS = {
    "search_stars",
    "search_upvotes",
    "get_item",
    "overview",
    "top_topics",
    "top_languages",
    "top_domains",
}


@pytest.fixture
def tokens_file(tmp_path):
    path = tmp_path / "tokens.json"
    path.write_text(json.dumps([{"name": "pim", "hash": hash_token("good-token")}]))
    return path


def _call(tool, **arguments):
    """Call a tool the way a client does and return the parsed payload."""
    blocks = asyncio.run(build_mcp().call_tool(tool, arguments))
    if isinstance(blocks, dict):
        return blocks
    return json.loads(blocks[0].text)


class TestEndpoints:
    def test_healthz_needs_no_credentials(self, tokens_file):
        with TestClient(build_app(tokens_file)) as client:
            response = client.get("/healthz")
        assert response.status_code == 200
        # Liveness only: nothing about the collection.
        assert response.json() == {"status": "ok"}

    def test_mcp_without_a_token_is_rejected(self, tokens_file):
        with TestClient(build_app(tokens_file)) as client:
            response = client.post("/mcp", json={})
        assert response.status_code == 401

    def test_rejection_carries_no_authentication_challenge(self, tokens_file):
        # A bare `Bearer` challenge names no realm and points at no metadata, so
        # it tells a client nothing — while sending one that follows the MCP
        # authorization flow off to look for OAuth metadata that does not exist.
        with TestClient(build_app(tokens_file)) as client:
            response = client.post("/mcp", json={})
        assert "www-authenticate" not in response.headers

    @pytest.mark.parametrize(
        "path",
        [
            "/.well-known/oauth-protected-resource",
            "/.well-known/oauth-protected-resource/mcp",
            "/.well-known/oauth-authorization-server",
            "/nope",
        ],
    )
    def test_unserved_paths_are_not_found_not_unauthorized(self, tokens_file, path):
        # 404 lets a client conclude there is no OAuth metadata and fall back to
        # its configured token. 401 left it unable to either discover or rule out
        # OAuth, so it gave up before trying the token at all.
        with TestClient(build_app(tokens_file)) as client:
            response = client.get(path)
        assert response.status_code == 404

    def test_an_unserved_path_discloses_nothing(self, tokens_file):
        with TestClient(build_app(tokens_file)) as client:
            response = client.get("/.well-known/oauth-protected-resource")
        assert response.status_code == 404
        assert "startaste" not in response.text.lower()

    def test_a_path_merely_prefixed_with_mcp_is_not_the_endpoint(self, tokens_file):
        # The guard matches "/mcp" and "/mcp/...", not any path starting with
        # those three letters.
        with TestClient(build_app(tokens_file)) as client:
            response = client.get("/mcpsomething")
        assert response.status_code == 404

    def test_mcp_with_a_wrong_token_is_rejected(self, tokens_file):
        with TestClient(build_app(tokens_file)) as client:
            response = client.post("/mcp", json={}, headers={"Authorization": "Bearer nope"})
        assert response.status_code == 401

    def test_mcp_with_a_valid_token_reaches_the_server(self, tokens_file):
        with TestClient(build_app(tokens_file)) as client:
            response = client.post("/mcp", json={}, headers={"Authorization": "Bearer good-token"})
        # Past authentication: the MCP layer rejects the empty body on its own
        # terms rather than the middleware returning 401.
        assert response.status_code != 401

    def test_no_usable_records_is_a_startup_error(self, tmp_path):
        path = tmp_path / "tokens.json"
        path.write_text("[]")
        with pytest.raises(SystemExit, match="no usable token records"):
            build_app(path)


class TestToolSurface:
    def test_exactly_the_expected_tools_with_descriptions(self):
        tools = asyncio.run(build_mcp().list_tools())
        assert {t.name for t in tools} == TOOLS
        assert all(t.description and t.description.strip() for t in tools)


class TestToolsAgainstData:
    def test_tools_return_empty_results_on_an_empty_database(self):
        assert _call("search_stars", query="x")["items"] == []
        assert _call("search_upvotes", query="x")["items"] == []
        assert _call("top_topics")["items"] == []
        assert _call("top_languages")["items"] == []
        assert _call("top_domains")["items"] == []
        assert _call("overview")["sources"]

    def test_search_and_aggregate_over_seeded_data(self):
        GithubStar.create(_id="1")
        GithubStar.save_doc({
            "id": "1", "time": "1700000000",
            "repo": {"full_name": "altsem/gitu", "description": "a git TUI",
                     "language": "Rust", "topics": ["git", "tui"]},
        })
        HnStory.create(_id="10")
        HnStory.save_doc({
            "id": "10", "time": "1700000000", "title": "Gitu is nice",
            "url": "https://example.com/x", "type": "story",
        })

        assert _call("search_stars", query="gitu")["items"][0]["full_name"] == "altsem/gitu"
        assert _call("search_upvotes", query="gitu")["items"][0]["id"] == "10"
        assert _call("top_topics")["items"][0]["count"] == 1
        assert _call("top_languages")["items"][0]["name"] == "Rust"
        assert _call("top_domains")["items"][0]["name"] == "example.com"

    def test_limit_is_respected_and_truncation_reported(self):
        for i in range(4):
            GithubStar.create(_id=str(i))
            GithubStar.save_doc({
                "id": str(i), "time": "1700000000",
                "repo": {"full_name": f"o/r{i}", "description": "shared word"},
            })
        result = _call("search_stars", query="shared", limit=2)
        assert len(result["items"]) == 2
        assert result["total"] == 4
        assert result["truncated"] is True

    def test_get_item_found_and_not_found(self):
        GithubStar.create(_id="1")
        GithubStar.save_doc({"id": "1", "time": "1700000000", "repo": {"full_name": "a/b"}})
        assert _call("get_item", source="github", item_id="1")["found"] is True
        missing = _call("get_item", source="github", item_id="404")
        assert missing["found"] is False
        assert "404" in missing["reason"]
