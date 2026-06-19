"""Safe-by-default модерация (инкремент 3, `08_implementation_plan.md`).

Rule-based классификатор без внешних сервисов: блок-листы по темам
(ненормативная лексика, политика, национальная вражда, грубый секс).
Точность намеренно консервативная — в safe-режиме лучше перестараться.
Стемминг/контекст не делаются (Фаза 2): matches по границам слов.

"badword" оставлен в списке как контрактный токен из test_api_contracts.py.
"""

import re

from app.schemas import GeneratePackRequest

# Жёстко блокируемые токены/темы в safe-режиме.
_BLOCKED_TOKENS = [
    # контрактный токен-заглушка (не убирать — защищает test_api_contracts.py)
    "badword",
    # ненормативная лексика
    "хуй", "пизда", "ебать", "ебан", "ёбан", "блядь", "блять", "пидор",
    "уебан", "сука", "гандон", "залупа",
    # политика / чувствительные темы
    "путин", "зеленский", "война", "нацист", "фашист", "путлер",
    # национальная / этническая вражда
    "чурка", "хачик", "жид", "хохол", "москаль",
    # грубый сексуальный контент
    "порно", "ххх",
]

_PATTERN = re.compile(
    r"\b(?:" + "|".join(re.escape(t) for t in _BLOCKED_TOKENS) + r")\b",
    re.IGNORECASE,
)

# В safe-режиме дерзость не выше этого уровня.
SAFE_MAX_BOLDNESS = 3


class ModerationError(RuntimeError):
    """Сгенерированный контент не прошёл модерацию (все кандидаты небезопасны)."""


def _contains_blocked(text: str) -> bool:
    return _PATTERN.search(text) is not None


def is_safe_input(request: GeneratePackRequest) -> bool:
    """Безопасен ли ввод (occasion + target + facts)."""
    joined = " ".join([request.occasion, request.target, *request.facts])
    return not _contains_blocked(joined)


def is_safe_text(text: str) -> bool:
    """Безопасен ли сгенерированный текст кандидата."""
    return not _contains_blocked(text)


def safe_boldness(boldness: int, *, safe_mode: bool) -> int:
    """Зажать дерзость в safe-режиме до SAFE_MAX_BOLDNESS."""
    return min(boldness, SAFE_MAX_BOLDNESS) if safe_mode else boldness