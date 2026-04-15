from collections.abc import Iterable

from app.schemas import Candidate, GeneratePackRequest, Pack


REFINE_SUFFIX = {
    "funnier": "Сделали версию повеселее.",
    "softer": "Сделали версию помягче.",
    "bolder": "Сделали версию подерзче.",
    "folksier": "Сделали версию понароднее.",
    "shorter": "Сделали версию покороче.",
    "more": "Сделали еще варианты.",
}

DISALLOWED_TOKENS = {"badword"}


class InMemoryPackStore:
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


def _compose_lines(request: GeneratePackRequest) -> Iterable[str]:
    facts = ", ".join(request.facts) if request.facts else "жизнь хороша"
    base = f"На {request.occasion} для {request.target}"
    for index in range(request.count):
        yield (
            f"{base}: факт {index + 1} — {facts}. "
            f"Тон: {request.tone}. Дерзость: {request.boldness}/5."
        )


def generate_pack(request: GeneratePackRequest, suffix: str = "") -> Pack:
    candidates: list[Candidate] = []
    for index, line in enumerate(_compose_lines(request)):
        score = round(1 - (index * 0.03), 3)
        safe = request.safe_mode or request.boldness <= 3
        text = f"{line} {suffix}".strip()
        candidates.append(
            Candidate(id=f"cand-{index + 1}", text=text, score=score, safe=safe),
        )
    ranked = sorted(candidates, key=lambda item: item.score, reverse=True)
    return Pack.new(ranked)


def is_safe_input(request: GeneratePackRequest) -> bool:
    joined = " ".join([request.occasion, request.target, *request.facts]).lower()
    return not any(token in joined for token in DISALLOWED_TOKENS)

