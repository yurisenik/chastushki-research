"""Хранилища паков.

`PackStore` — интерфейс, который дёргает `app.api.routes`. Две реализации:
- `InMemoryPackStore` — без БД, по умолчанию (локальная разработка и контрактные
  тесты). Поведение как у прежней заглушки из `pipeline.py`.
- `PostgresPackStore` — поверх SQLAlchemy/Postgres; включается через DATABASE_URL.

`get_store()` — фабрика-синглтон (FastAPI-зависимость), выбирает реализацию по
окружению. Как и `get_llm`, кэшируется (`lru_cache`), поэтому смена DATABASE_URL
в рамках процесса требует `get_store.cache_clear()`.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Optional

from app.schemas import Candidate, Pack


class PackStore(ABC):
    """Интерфейс хранилища паков, истории, избранного и метрик."""

    @abstractmethod
    def save_pack(self, pack: Pack) -> None: ...

    @abstractmethod
    def get_pack(self, pack_id: str) -> Pack:
        """Вернуть пак по id; `KeyError`, если не найден."""

    @abstractmethod
    def history(self) -> list[Pack]: ...

    @abstractmethod
    def add_favorite(self, pack_id: str) -> Pack:
        """Добавить пак в избранное (идемпотентно); `KeyError`, если не найден."""

    @abstractmethod
    def favorites(self) -> list[Pack]: ...

    @abstractmethod
    def metrics(self) -> dict[str, float]: ...


class InMemoryPackStore(PackStore):
    """Процесс-локальное хранилище; всё теряется при рестарте."""

    def __init__(self) -> None:
        self._history: list[Pack] = []
        self._by_id: dict[str, Pack] = {}
        self._favorites: list[Pack] = []
        self._metrics: dict[str, int] = {
            "generate_count": 0,
            "refine_count": 0,
            "favorite_count": 0,
        }

    def save_pack(self, pack: Pack) -> None:
        self._history.insert(0, pack)
        self._by_id[pack.pack_id] = pack
        if pack.source_pack_id:
            self._metrics["refine_count"] += 1
        else:
            self._metrics["generate_count"] += 1

    def get_pack(self, pack_id: str) -> Pack:
        return self._by_id[pack_id]

    def history(self) -> list[Pack]:
        return self._history

    def add_favorite(self, pack_id: str) -> Pack:
        pack = self.get_pack(pack_id)
        if not any(item.pack_id == pack_id for item in self._favorites):
            self._favorites.insert(0, pack)
            self._metrics["favorite_count"] += 1
        return pack

    def favorites(self) -> list[Pack]:
        return self._favorites

    def metrics(self) -> dict[str, float]:
        generated = max(self._metrics["generate_count"], 1)
        usable_output_rate = min(
            1.0,
            round((self._metrics["favorite_count"] / generated), 3),
        )
        return {
            **self._metrics,
            "usable_output_rate": usable_output_rate,
        }


@lru_cache
def get_store() -> PackStore:
    """Фабрика хранилища: Postgres при DATABASE_URL, иначе in-memory."""
    if os.getenv("DATABASE_URL"):
        # импорт отложенный — чтобы модуль можно было импортировать без SQLAlchemy
        from app.services.db_store import PostgresPackStore

        return PostgresPackStore()
    return InMemoryPackStore()


# Для удобства тестов/тайпингов — реэкспорт, чтобы не плодить import-циклы.
__all__ = ["PackStore", "InMemoryPackStore", "get_store", "Candidate", "Pack", "Optional"]