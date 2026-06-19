"""initial schema: packs, candidates, favorites

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-20 00:00:00

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "packs",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("pack_id", sa.String, nullable=False),
        sa.Column("source_pack_id", sa.String, nullable=True),
        sa.Column("created_at", sa.String, nullable=False),
        sa.UniqueConstraint("pack_id", name="uq_packs_pack_id"),
    )
    op.create_index("ix_packs_pack_id", "packs", ["pack_id"])

    op.create_table(
        "candidates",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "pack_id",
            sa.String,
            sa.ForeignKey("packs.pack_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("cand_id", sa.String, nullable=False),
        sa.Column("text", sa.String, nullable=False),
        sa.Column("score", sa.Float, nullable=False),
        sa.Column("safe", sa.Boolean, nullable=False),
        sa.Column("position", sa.Integer, nullable=False),
    )
    op.create_index("ix_candidates_pack_id", "candidates", ["pack_id"])

    op.create_table(
        "favorites",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column(
            "pack_id",
            sa.String,
            sa.ForeignKey("packs.pack_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.String, nullable=False),
        sa.UniqueConstraint("pack_id", name="uq_favorites_pack_id"),
    )


def downgrade() -> None:
    op.drop_table("favorites")
    op.drop_index("ix_candidates_pack_id", table_name="candidates")
    op.drop_table("candidates")
    op.drop_index("ix_packs_pack_id", table_name="packs")
    op.drop_table("packs")