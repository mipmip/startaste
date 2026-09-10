"""Bearer-token authentication for the MCP endpoint.

Mirrors linny-mcp-server/internal/auth so both services on the same host behave
identically: records of {name, hash, scopes} where hash is the hex SHA-256 of
the raw token, compared in constant time without early exit, behind a single
indistinguishable failure.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import secrets
from dataclasses import dataclass, field
from pathlib import Path

log = logging.getLogger(__name__)

TOKEN_BYTES = 32  # 256 bits of entropy


class Unauthorized(Exception):
    """The single failure for every rejection.

    Deliberately singular: callers must not be able to distinguish a missing,
    malformed, unknown or wrong token.
    """


@dataclass(frozen=True)
class Identity:
    name: str
    scopes: tuple[str, ...] = ()


@dataclass(frozen=True)
class TokenRecord:
    name: str
    hash: str
    # Accepted and stored but unused: every tool is read-only today. Parsing it
    # now means adding a write tool later needs no token-file migration.
    scopes: tuple[str, ...] = field(default=())


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def generate_token() -> str:
    """A fresh token with at least 256 bits of entropy, base64url, no padding."""
    return secrets.token_urlsafe(TOKEN_BYTES)


def parse_bearer(header: str | None) -> str:
    """Extract the token from an Authorization header. Fails closed."""
    scheme = "bearer "
    if not header or len(header) <= len(scheme):
        raise Unauthorized()
    if header[: len(scheme)].lower() != scheme:
        raise Unauthorized()
    token = header[len(scheme):].strip()
    if not token:
        raise Unauthorized()
    return token


def load_records(path: str | Path) -> list[TokenRecord]:
    """Read token records from a JSON file: a list, or {"tokens": [...]}.

    A malformed record is skipped with a warning rather than rejected, so one
    bad entry cannot take down the valid tokens beside it.
    """
    path = Path(path)
    try:
        raw = json.loads(path.read_text())
    except FileNotFoundError:
        raise SystemExit(f"Error: no token file at {path}")
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Error: cannot read token file {path}: {exc}")

    entries = raw.get("tokens", []) if isinstance(raw, dict) else raw
    if not isinstance(entries, list):
        raise SystemExit(f"Error: token file {path} must hold a list of records")

    records = []
    for entry in entries:
        if not isinstance(entry, dict):
            log.warning("skipping malformed token record: not an object")
            continue
        name, digest = entry.get("name"), entry.get("hash")
        if not isinstance(name, str) or not isinstance(digest, str) or not digest:
            log.warning("skipping malformed token record %r", name)
            continue
        scopes = entry.get("scopes") or []
        records.append(TokenRecord(
            name=name,
            hash=digest,
            scopes=tuple(s for s in scopes if isinstance(s, str)),
        ))
    return records


class StaticTokenAuthenticator:
    """Authenticates against a fixed set of hashed tokens."""

    def __init__(self, records: list[TokenRecord]) -> None:
        self._records = list(records)

    def authenticate(self, token: str) -> Identity:
        digest = hash_token(token)

        matched: TokenRecord | None = None
        for record in self._records:
            # compare_digest on every record, never breaking early, so timing
            # does not reveal which record (if any) matched.
            if hmac.compare_digest(digest, record.hash):
                matched = record

        if matched is None:
            raise Unauthorized()
        return Identity(name=matched.name, scopes=matched.scopes)

    def authenticate_header(self, header: str | None) -> Identity:
        return self.authenticate(parse_bearer(header))
