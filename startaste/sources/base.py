from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from startaste.db import Doc


class SourceError(Exception):
    """A source could not complete its sync.

    Carries enough for the caller to write one clean line: which source, and
    what the operator should do about it. Sources raise these instead of letting
    a transport exception escape, so `sync` never shows a traceback for a
    condition it understands.
    """

    def __init__(self, source: str, detail: str) -> None:
        self.source = source
        self.detail = detail
        super().__init__(f"{source}: {detail}")


class SourceAuthError(SourceError):
    """The source rejected the credentials it was given.

    Distinct from a missing credential (reported before any request) and from a
    source being unavailable — the operator has to renew something.
    """

    def __init__(self, source: str, detail: str, env_vars: list[str] | None = None) -> None:
        self.env_vars = list(env_vars or [])
        super().__init__(source, detail)


class SourceUnavailableError(SourceError):
    """The source could not be reached, or refused because of rate limiting.

    Transient: nothing is wrong with the credentials, and retrying later is the
    right response.
    """


class Source:
    name: str
    item_types: list[str]
    models: list[type[Doc]]
    env_help: dict[str, str]

    def is_configured(self) -> bool:
        raise NotImplementedError

    def sync(self) -> None:
        raise NotImplementedError
