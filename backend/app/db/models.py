"""ORM-модели: паки, кандидаты, избранное.

Схема:
- `packs` — строка на пак; `id` BIGSERIAL даёт стабильный порядок истории
  (новые = больше id), `pack_id` — публичный идентификатор.
- `candidates` — строки пака; `position` сохраняет порядок внутри пака.
- `favorites` — избранное; `pack_id` UNIQUE делает любимое идемпотентным,
  `id` BIGSERIAL — порядок (новые = больше id).

Метрики (`/v1/metrics`) выводятся из этих таблиц, а не хранятся счётчиками.
"""

from __future__ import annotations

from sqlalchemy import BigInteger, Boolean, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Pack(Base):
    __tablename__ = "packs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pack_id: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    source_pack_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False)

    candidates: Mapped[list["Candidate"]] = relationship(
        back_populates="pack",
        cascade="all, delete-orphan",
        order_by="Candidate.position",
        lazy="selectin",
    )


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pack_id: Mapped[str] = mapped_column(
        String, ForeignKey("packs.pack_id", ondelete="CASCADE"), nullable=False, index=True
    )
    cand_id: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    safe: Mapped[bool] = mapped_column(Boolean, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    pack: Mapped[Pack] = relationship(back_populates="candidates")


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pack_id: Mapped[str] = mapped_column(
        String, ForeignKey("packs.pack_id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (UniqueConstraint("pack_id", name="uq_favorites_pack_id"),)