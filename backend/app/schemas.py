from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class GeneratePackRequest(BaseModel):
    occasion: str
    target: str
    facts: list[str] = Field(default_factory=list)
    tone: str = "funny"
    boldness: int = Field(default=2, ge=0, le=5)
    safe_mode: bool = True
    count: int = Field(default=6, ge=3, le=20)


class Candidate(BaseModel):
    id: str
    text: str
    score: float
    safe: bool


class Pack(BaseModel):
    pack_id: str
    source_pack_id: str | None = None
    candidates: list[Candidate]
    created_at: str

    @staticmethod
    def new(candidates: list[Candidate], source_pack_id: str | None = None) -> "Pack":
        return Pack(
            pack_id=str(uuid4()),
            source_pack_id=source_pack_id,
            candidates=candidates,
            created_at=datetime.now(tz=timezone.utc).isoformat(),
        )


class RefineRequest(BaseModel):
    pack_id: str
    action: Literal["funnier", "softer", "bolder", "folksier", "shorter", "more"]


class FavoriteRequest(BaseModel):
    pack_id: str


class HistoryResponse(BaseModel):
    items: list[Pack]

