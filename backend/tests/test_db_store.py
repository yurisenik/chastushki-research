"""Тесты PostgresPackStore против настоящей тестовой БД.

Запускаются только когда задан DATABASE_URL (CI поднимает postgres-сервис).
Локально без БД — пропускаются, чтобы `make test` оставался зелёным.

Схема поднимается через `Base.metadata.create_all` (не через Alembic) —
миграции проверяются в docker, а здесь нам нужен только быстрый round-trip.
"""

from __future__ import annotations

import os

import pytest

from app.db import session as db_session
from app.db.session import Base
from app.schemas import Candidate, Pack
from app.services.db_store import PostgresPackStore

DATABASE_URL = os.getenv("DATABASE_URL")
pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="DATABASE_URL не задан — тесты Postgres-хранилища пропускаются",
)


@pytest.fixture()
def db_schema():
    # engine/SessionLocal резолвятся лениво — только если тест реально запустился.
    engine = db_session.engine
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


def _pack(pack_id: str = "pack-1", source: str | None = None) -> Pack:
    candidates = [
        Candidate(id=f"cand-{i}", text=f"строка {i}\nвторая", score=1.0 - i * 0.1, safe=True)
        for i in range(1, 4)
    ]
    return Pack(
        pack_id=pack_id,
        source_pack_id=source,
        candidates=candidates,
        created_at="2026-06-20T00:00:00+00:00",
    )


def test_save_and_get_pack_round_trip(db_schema):
    store = PostgresPackStore()
    pack = _pack()
    store.save_pack(pack)

    fetched = store.get_pack("pack-1")
    assert fetched.pack_id == "pack-1"
    assert fetched.source_pack_id is None
    assert [c.id for c in fetched.candidates] == ["cand-1", "cand-2", "cand-3"]
    assert fetched.candidates[0].text == "строка 1\nвторая"
    assert fetched.candidates[0].score == pytest.approx(0.9)
    assert all(c.safe for c in fetched.candidates)


def test_get_pack_missing_raises_key_error(db_schema):
    store = PostgresPackStore()
    with pytest.raises(KeyError):
        store.get_pack("no-such-pack")


def test_history_is_newest_first(db_schema):
    store = PostgresPackStore()
    store.save_pack(_pack("pack-a"))
    store.save_pack(_pack("pack-b"))
    store.save_pack(_pack("pack-c"))

    ids = [p.pack_id for p in store.history()]
    assert ids == ["pack-c", "pack-b", "pack-a"]


def test_add_favorite_is_idempotent_and_does_not_double_count(db_schema):
    store = PostgresPackStore()
    store.save_pack(_pack("pack-1"))

    first = store.add_favorite("pack-1")
    second = store.add_favorite("pack-1")
    assert first.pack_id == second.pack_id == "pack-1"

    favorites = store.favorites()
    assert [p.pack_id for p in favorites] == ["pack-1"]
    assert len(favorites) == 1
    # повторное добавление не должно увеличить счётчик
    assert store.metrics()["favorite_count"] == 1


def test_add_favorite_missing_raises_key_error(db_schema):
    store = PostgresPackStore()
    with pytest.raises(KeyError):
        store.add_favorite("no-such-pack")


def test_metrics_counts_generate_refine_and_favorite(db_schema):
    store = PostgresPackStore()
    store.save_pack(_pack("g-1"))
    store.save_pack(_pack("g-2"))
    store.save_pack(_pack("r-1", source="g-1"))  # refine
    store.add_favorite("g-1")

    metrics = store.metrics()
    assert metrics["generate_count"] == 2
    assert metrics["refine_count"] == 1
    assert metrics["favorite_count"] == 1
    assert metrics["usable_output_rate"] == pytest.approx(min(1.0, round(1 / 2, 3)))


def test_metrics_usable_output_rate_floor_when_no_favorites(db_schema):
    store = PostgresPackStore()
    store.save_pack(_pack("g-1"))
    metrics = store.metrics()
    assert metrics["generate_count"] == 1
    assert metrics["favorite_count"] == 0
    assert metrics["usable_output_rate"] == 0.0


def test_refine_pack_counts_as_refine_not_generate(db_schema):
    store = PostgresPackStore()
    store.save_pack(_pack("g-1"))
    store.save_pack(_pack("r-1", source="g-1"))

    metrics = store.metrics()
    assert metrics["generate_count"] == 1
    assert metrics["refine_count"] == 1