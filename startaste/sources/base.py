from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from startaste.db import Doc


class Source:
    name: str
    item_types: list[str]
    models: list[type[Doc]]
    env_help: dict[str, str]

    def is_configured(self) -> bool:
        raise NotImplementedError

    def sync(self) -> None:
        raise NotImplementedError
