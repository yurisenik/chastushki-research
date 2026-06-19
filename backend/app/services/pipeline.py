from app.schemas import Candidate, GeneratePackRequest, Pack
from app.services.form import score_candidate
from app.services.llm import ChastushkaLLM, LLMError


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


def generate_pack(
    request: GeneratePackRequest,
    suffix: str = "",
    *,
    llm: ChastushkaLLM,
) -> Pack:
    """Сгенерировать пак частушек через LLM, оценить по форме и ранжировать.

    Скоринг по форме (инкремент 2, `08_implementation_plan.md` Этап C/D):
    composite из ритма и рифмы; кандидаты сортируются по убыванию score,
    так что плохая форма тонет на дно. `safe` пока эвристический — реальная
    модерация в инкременте 3.
    """
    chastushki = llm.generate(request, suffix)
    if len(chastushki) < request.count:
        raise LLMError(
            f"модель вернула {len(chastushki)} частушек, ожидалось {request.count}"
        )
    chastushki = chastushki[: request.count]

    safe = request.safe_mode or request.boldness <= 3
    candidates: list[Candidate] = [
        Candidate(
            id="cand-placeholder",
            text="\n".join(lines),
            score=score_candidate("\n".join(lines)),
            safe=safe,
        )
        for lines in chastushki
    ]
    # ранжирование по форме (стабильно — равные score сохраняют порядок модели)
    candidates.sort(key=lambda c: c.score, reverse=True)
    for index, candidate in enumerate(candidates):
        candidate.id = f"cand-{index + 1}"
    return Pack.new(candidates)


def is_safe_input(request: GeneratePackRequest) -> bool:
    joined = " ".join([request.occasion, request.target, *request.facts]).lower()
    return not any(token in joined for token in DISALLOWED_TOKENS)
