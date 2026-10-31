"""Local-ID permutation harness for SRQ-01 AC3/AC4 (test utility, not a test).

``permuted_reference_session(seed)`` yields a Session in which every local
material ID of the loaded reference dataset is replaced by a seed-controlled
permutation of the same IDs, with every foreign key rewritten to match. MP IDs
and all other column values are unchanged, so results can be compared by MP ID.

Integrity and isolation:
  * The whole rewrite runs inside one outer transaction on one connection and
    is rolled back on exit, DDL included. Nothing is committed, so the IDs the
    golden suite depends on (1-28) are never changed for other connections.
  * Foreign keys referencing ``materials.id`` are discovered from the catalog,
    dropped, rewritten and re-added with their original definitions. Re-adding
    makes PostgreSQL re-validate every row, so a broken reference fails here.
  * After rollback the context manager re-reads the reference identities on a
    fresh connection and fails if any ID-to-MP-ID pairing differs.
"""

from __future__ import annotations

import random
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import engine

OFFSET = 1_000_000
BASELINE = "baseline"
REVERSED = "reversed"


def _identity_map(connection) -> dict[int, str]:
    return dict(connection.execute(text("SELECT id, mp_id FROM materials ORDER BY id")).all())


def permutation(ids: list[int], seed: int | str) -> dict[int, int]:
    """Old ID -> new ID: a permutation of the same ID set.

    ``"baseline"`` is the identity; ``"reversed"`` maps the lowest ID to the
    highest; an integer seeds ``random.Random`` for a reproducible shuffle.
    """
    ordered = sorted(ids)
    if seed == BASELINE:
        shuffled = list(ordered)
    elif seed == REVERSED:
        shuffled = list(reversed(ordered))
    else:
        shuffled = list(ordered)
        random.Random(seed).shuffle(shuffled)
    return dict(zip(ordered, shuffled))


def _referencing_foreign_keys(connection) -> list[tuple[str, str, str, str]]:
    """(table, constraint, column, definition) for every FK to materials.id."""
    rows = connection.execute(text(
        """
        SELECT c.conrelid::regclass::text, c.conname, a.attname,
               pg_get_constraintdef(c.oid)
        FROM pg_constraint c
        JOIN pg_attribute a
          ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]
        WHERE c.contype = 'f' AND c.confrelid = 'materials'::regclass
          AND array_length(c.conkey, 1) = 1
        ORDER BY 1, 2
        """
    )).all()
    return [tuple(row) for row in rows]


def _remap(connection, table: str, column: str, mapping: dict[int, int]) -> None:
    # Two passes through a disjoint offset range so no intermediate value can
    # collide with an ID that is still in use.
    connection.execute(text(
        f'UPDATE {table} SET "{column}" = "{column}" + :offset '
        f'WHERE "{column}" IS NOT NULL'
    ), {"offset": OFFSET})
    cases = " ".join(f"WHEN {old + OFFSET} THEN {new}" for old, new in mapping.items())
    connection.execute(text(
        f'UPDATE {table} SET "{column}" = CASE "{column}" {cases} END '
        f'WHERE "{column}" IS NOT NULL'
    ))


@contextmanager
def permuted_reference_session(seed: int | str) -> Iterator[tuple[Session, dict[int, int]]]:
    """Yield (session, old->new ID mapping) with permuted local IDs; roll back after."""
    before = None
    connection = engine.connect()
    outer = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        before = _identity_map(connection)
        mapping = permutation(list(before), seed)
        if seed != BASELINE:
            foreign_keys = _referencing_foreign_keys(connection)
            for table, constraint, _column, _definition in foreign_keys:
                connection.execute(text(f'ALTER TABLE {table} DROP CONSTRAINT "{constraint}"'))
            _remap(connection, "materials", "id", mapping)
            for table, _constraint, column, _definition in foreign_keys:
                _remap(connection, table, column, mapping)
            for table, constraint, _column, definition in foreign_keys:
                connection.execute(text(f'ALTER TABLE {table} ADD CONSTRAINT "{constraint}" {definition}'))
        after = _identity_map(connection)
        assert {mapping[old]: mp_id for old, mp_id in before.items()} == after, "permutation lost a material"
        yield session, mapping
    finally:
        session.close()
        if outer.is_active:
            outer.rollback()
        connection.close()
        if before is not None:
            with engine.connect() as check:
                assert _identity_map(check) == before, "permutation was not rolled back"
