"""Postgres-реализация `PackStore` поверх SQLAlchemy.

Одна сессия на вызов метода. Метрики выводятся из таблиц запросами, а не
хранятся счётчиками — поэтому они согласованы с реальными данными после рестарта.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select

from app.db.models import Candidate as CandidateRow
from app.db.models import Favorite, Pack as PackRow
from app.db.session import get_session
from app.schemas import Candidate, Pack
from app.services.store import PackStore


class PostgresPackStore(PackStore):
    """Хранилище паков в Postgres; переживает рестарт процесса."""

    def save_pack(self, pack: Pack) -> None:
        with get_session() as session:
            row = PackRow(
                pack_id=pack.pack_id,
                source_pack_id=pack.source_pack_id,
                created_at=pack.created_at,
            )
            session.add(row)
            session.add_all(
                CandidateRow(
                    pack_id=pack.pack_id,
                    cand_id=c.id,
                    text=c.text,
                    score=c.score,
                    safe=c.safe,
                    position=index,
                )
                for index, c in enumerate(pack.candidates)
            )
            session.commit()

    def get_pack(self, pack_id: str) -> Pack:
        with get_session() as session:
            row = session.scalars(select(PackRow).where(PackRow.pack_id == pack_id)).first()
            if row is None:
                raise KeyError(pack_id)
            return _row_to_pack(row)

    def history(self) -> list[Pack]:
        with get_session() as session:
            rows = session.scalars(select(PackRow).order_by(PackRow.id.desc())).all()
            return [_row_to_pack(r) for r in rows]

    def add_favorite(self, pack_id: str) -> Pack:
        with get_session() as session:
            row = session.scalars(select(PackRow).where(PackRow.pack_id == pack_id)).first()
            if row is None:
                raise KeyError(pack_id)
            # идемпотентно: ON CONFLICT (pack_id) DO NOTHING
            existing = session.scalars(
                select(Favorite).where(Favorite.pack_id == pack_id)
            ).first()
            if existing is None:
                session.add(
                    Favorite(
                        pack_id=pack_id,
                        created_at=datetime.now(tz=timezone.utc).isoformat(),
                    )
                )
                session.commit()
            return _row_to_pack(row)

    def favorites(self) -> list[Pack]:
        with get_session() as session:
            rows = session.scalars(
                select(PackRow)
                .join(Favorite, Favorite.pack_id == PackRow.pack_id)
                .order_by(Favorite.id.desc())
            ).all()
            return [_row_to_pack(r) for r in rows]

    def metrics(self) -> dict[str, float]:
        with get_session() as session:
            generate_count = session.scalar(
                select(func.count()).select_from(PackRow).where(PackRow.source_pack_id.is_(None))
            ) or 0
            refine_count = session.scalar(
                select(func.count())
                .select_from(PackRow)
                .where(PackRow.source_pack_id.is_not(None))
            ) or 0
            favorite_count = session.scalar(
                select(func.count()).select_from(Favorite)
            ) or 0
        usable_output_rate = min(1.0, round(favorite_count / max(generate_count, 1), 3))
        return {
            "generate_count": int(generate_count),
            "refine_count": int(refine_count),
            "favorite_count": int(favorite_count),
            "usable_output_rate": usable_output_rate,
        }


def _row_to_pack(row: PackRow) -> Pack:
    candidates = [
        Candidate(id=c.cand_id, text=c.text, score=c.score, safe=c.safe)
        for c in row.candidates
    ]
    return Pack(
        pack_id=row.pack_id,
        source_pack_id=row.source_pack_id,
        candidates=candidates,
        created_at=row.created_at,
    )