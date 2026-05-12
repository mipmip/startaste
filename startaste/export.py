from __future__ import annotations

import json
import logging

from startaste.sources import get_sources, get_source

log = logging.getLogger(__name__)


def _pluralize(type_name: str) -> str:
    if type_name.endswith("y"):
        return type_name[:-1] + "ies"
    return type_name + "s"


def run_export(
    format: str = "json",
    source: str | None = None,
    type: str | None = None,
    file: str | None = None,
):
    if source:
        sources = [get_source(source)]
    else:
        sources = get_sources()

    result = {}
    for src in sources:
        src_data = {}
        for model, item_type in zip(src.models, src.item_types):
            if type and item_type != type:
                continue
            key = _pluralize(item_type)
            src_data[key] = model.to_dict()
        if src_data:
            result[src.name] = src_data

    output = json.dumps(result, indent=2)

    if file:
        with open(file, "w") as f:
            f.write(output)
        log.info(f"Exported to {file}")
    else:
        print(output)
