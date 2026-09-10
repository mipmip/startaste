import json

import pytest

from startaste.mcp.auth import (
    StaticTokenAuthenticator,
    TokenRecord,
    Unauthorized,
    generate_token,
    hash_token,
    load_records,
)


def _records_file(tmp_path, entries):
    path = tmp_path / "tokens.json"
    path.write_text(json.dumps(entries))
    return path


class TestFailuresAreIndistinguishable:
    """Missing, malformed, unknown and wrong must all fail the same way."""

    @pytest.fixture
    def auth(self):
        return StaticTokenAuthenticator([TokenRecord(name="pim", hash=hash_token("good"))])

    @pytest.mark.parametrize(
        "header",
        [None, "", "Bearer", "Bearer ", "Basic good", "bearer wrong", "good"],
        ids=["missing", "empty", "scheme-only", "no-token", "wrong-scheme", "wrong-token", "no-scheme"],
    )
    def test_every_failure_raises_the_same_exception(self, auth, header):
        with pytest.raises(Unauthorized) as excinfo:
            auth.authenticate_header(header)
        # Nothing in the failure distinguishes the cause.
        assert str(excinfo.value) == ""

    def test_valid_token_is_accepted(self, auth):
        assert auth.authenticate_header("Bearer good").name == "pim"

    def test_scheme_match_is_case_insensitive(self, auth):
        assert auth.authenticate_header("bEaReR good").name == "pim"


class TestConstantTimeComparison:
    def test_every_record_is_compared(self, monkeypatch):
        """No early exit: a match in the first record must not skip the rest."""
        compared = []
        import startaste.mcp.auth as auth_mod

        real = auth_mod.hmac.compare_digest

        def counting(a, b):
            compared.append(b)
            return real(a, b)

        monkeypatch.setattr(auth_mod.hmac, "compare_digest", counting)
        records = [
            TokenRecord(name="first", hash=hash_token("good")),
            TokenRecord(name="second", hash=hash_token("other")),
            TokenRecord(name="third", hash=hash_token("third")),
        ]
        StaticTokenAuthenticator(records).authenticate("good")
        assert len(compared) == 3


class TestRecordLoading:
    def test_loads_a_list(self, tmp_path):
        path = _records_file(tmp_path, [{"name": "pim", "hash": hash_token("t"), "scopes": ["read"]}])
        records = load_records(path)
        assert records[0].name == "pim"
        assert records[0].scopes == ("read",)

    def test_loads_a_tokens_object(self, tmp_path):
        path = _records_file(tmp_path, {"tokens": [{"name": "pim", "hash": hash_token("t")}]})
        assert load_records(path)[0].name == "pim"

    def test_malformed_record_is_skipped_and_valid_ones_still_work(self, tmp_path):
        path = _records_file(tmp_path, [
            {"name": "broken"},                     # no hash
            "not-an-object",
            {"hash": hash_token("x")},              # no name
            {"name": "good", "hash": hash_token("works")},
        ])
        records = load_records(path)
        assert [r.name for r in records] == ["good"]
        assert StaticTokenAuthenticator(records).authenticate("works").name == "good"

    def test_malformed_record_never_authenticates(self, tmp_path):
        path = _records_file(tmp_path, [{"name": "broken", "hash": ""}])
        records = load_records(path)
        with pytest.raises(Unauthorized):
            StaticTokenAuthenticator(records).authenticate("")

    def test_missing_file_is_a_clear_error(self, tmp_path):
        with pytest.raises(SystemExit, match="no token file"):
            load_records(tmp_path / "absent.json")

    def test_unreadable_content_is_a_clear_error(self, tmp_path):
        path = tmp_path / "tokens.json"
        path.write_text("{not json")
        with pytest.raises(SystemExit, match="cannot read token file"):
            load_records(path)


class TestGeneratedTokens:
    def test_entropy_and_uniqueness(self):
        tokens = {generate_token() for _ in range(50)}
        assert len(tokens) == 50
        assert all(len(t) >= 43 for t in tokens)  # 32 bytes base64url, unpadded

    def test_hash_matches_the_token(self):
        token = generate_token()
        record = TokenRecord(name="pim", hash=hash_token(token))
        assert StaticTokenAuthenticator([record]).authenticate(token).name == "pim"
