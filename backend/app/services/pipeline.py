from app.schemas import Candidate, GeneratePackRequest, Pack
from app.services.form import score_candidate
from app.services.llm import ChastushkaLLM, LLMError
from app.services.moderation import ModerationError, is_safe_text, safe_boldness


REFINE_SUFFIX = {
    "funnier": "Сделали версию повеселее.",
    "softer": "Сделали версию помягче.",
    "bolder": "Сделали версию подерзче.",
    "folksier": "Сделали версию понароднее.",
    "shorter": "Сделали версию покороче.",
    "more": "Сделали еще варианты.",
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
    так что плохая форма тонет на дно.

    Модерация (инкремент 3): в safe-режиме дерзость зажимается до 3 и
    небезопасные кандидаты отбраковываются; если не выжил ни один —
    `ModerationError`. Флаг `safe` = прошёл модерацию (или дерзость <= 3
    вне safe-режима).
    """
    effective_request = request.model_copy(
        update={"boldness": safe_boldness(request.boldness, safe_mode=request.safe_mode)}
    )

    chastushki = llm.generate(effective_request, suffix)
    if len(chastushki) < request.count:
        raise LLMError(
            f"модель вернула {len(chastushki)} частушек, ожидалось {request.count}"
        )
    chastushki = chastushki[: request.count]

    safe_flag = request.safe_mode or effective_request.boldness <= 3
    candidates: list[Candidate] = []
    for lines in chastushki:
        text = "\n".join(lines)
        if request.safe_mode and not is_safe_text(text):
            continue  # отбраковка небезопасного вывода в safe-режиме
        candidates.append(
            Candidate(
                id="cand-placeholder",
                text=text,
                score=score_candidate(text),
                safe=safe_flag,
            )
        )
    if not candidates:
        raise ModerationError("все кандидаты не прошли модерацию")

    # ранжирование по форме (стабильно — равные score сохраняют порядок модели)
    candidates.sort(key=lambda c: c.score, reverse=True)
    for index, candidate in enumerate(candidates):
        candidate.id = f"cand-{index + 1}"
    return Pack.new(candidates)
