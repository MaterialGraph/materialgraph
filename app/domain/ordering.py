"""Stable ordering keys and conventions (SRQ-01 spec, R3, R5).

Pure functions only: no database, model or service imports, so every layer
can use them without depending on one another.
"""

import re

_MP_ID = re.compile(r"^mp-(\d+)$")


def mp_id_sort_key(mp_id: str | None, material_id: int) -> tuple:
    """R5: numeric MP ID first; other IDs after, by string, then local ID.

    The local ID is a last, documented fallback. ``materials.mp_id`` is unique
    and every current ID matches ``^mp-\\d+$``, so it is unreachable on current
    data; a test fails if an objective-aware ordering decision ever uses it.
    """
    match = _MP_ID.match(mp_id or "")
    if match:
        return (0, int(match.group(1)), "", material_id)
    return (1, 0, mp_id or "", material_id)


def choose_representative(members: list[dict]) -> dict:
    """R3: the formula-group member that is traversed and scored.

    The record with the lowest MP-ID key. This is a reproducibility
    convention, not a scientific preference. Kept as a single module-level
    function so the AC11 sensitivity check can substitute each member in turn.
    """
    return min(members, key=lambda member: mp_id_sort_key(member.get("mp_id"), member["material_id"]))
