"""SQLAlchemy-сессия поверх Postgres.

Движок строится из `DATABASE_URL` (вид `postgresql+psycopg://...`).
`engine` и `SessionLocal` — ленивые модульные атрибуты (PEP 562): создаются при
первом обращении, поэтому импорт модуля работает и без БД / без DATABASE_URL.

Тесты и миграции используют `Base.metadata.create_all(engine)` / `SessionLocal()`.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Базовый класс всех ORM-моделей."""


_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def _build() -> tuple[Engine, sessionmaker[Session]]:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL не задан — Postgres-хранилище недоступно")
    eng = create_engine(url, pool_pre_ping=True, future=True)
    return eng, sessionmaker(bind=eng, autoflush=False, autocommit=False, future=True)


def _ensure() -> tuple[Engine, sessionmaker[Session]]:
    global _engine, _SessionLocal
    if _engine is None or _SessionLocal is None:
        _engine, _SessionLocal = _build()
    return _engine, _SessionLocal  # type: ignore[return-value]


def __getattr__(name: str) -> Any:
    """Лениво резолвим `engine` и `SessionLocal` как модульные атрибуты."""
    if name == "engine":
        return _ensure()[0]
    if name == "SessionLocal":  # noqa: N816 - публичное имя
        return _ensure()[1]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def get_session() -> Session:
    """Создать новую сессию. Вызывающий отвечает за закрытие."""
    return _ensure()[1]()


def get_db() -> Iterator[Session]:
    """FastAPI-зависимость: сессия на запрос."""
    session = _ensure()[1]()
    try:
        yield session
    finally:
        session.close()


if TYPE_CHECKING:
    # Подсказки типам: реальные значения резолвятся через __getattr__.
    engine: Engine
    SessionLocal: sessionmaker[Session]