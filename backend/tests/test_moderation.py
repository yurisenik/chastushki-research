"""Тесты модерации (инкремент 3): safe-by-default rule-based классификатор.

Без сети и внешних сервисов: блок-лист по темам (ненормативная лексика,
политика, национальная вражда, грубый секс). В safe-режиме режется и ввод,
и сгенерированный текст; boldness зажимается до 3.
"""

import pytest

from app.schemas import GeneratePackRequest
from app.services.llm import ChastushkaLLM
from app.services.moderation import (
    ModerationError,
    is_safe_input,
    is_safe_text,
    safe_boldness,
)


def _request(**overrides) -> GeneratePackRequest:
    base = dict(
        occasion="юбилей",
        target="Иван",
        facts=["любит рыбалку"],
        tone="funny",
        boldness=2,
        safe_mode=True,
        count=3,
    )
    base.update(overrides)
    return GeneratePackRequest(**base)


# --- ввод ----------------------------------------------------------------


def test_safe_input_passes_benign_request():
    assert is_safe_input(_request()) is True


def test_safe_input_blocks_legacy_badword_token():
    # контракт из test_api_contracts.py: "badword" должен оставаться блокированным
    assert is_safe_input(_request(facts=["badword"])) is False


def test_safe_input_blocks_profanity_in_any_field():
    assert is_safe_input(_request(occasion="ебать веселье")) is False
    assert is_safe_input(_request(target="сука")) is False
    assert is_safe_input(_request(facts=["да пошёл ты на хуй"])) is False


def test_safe_input_blocks_political_and_hate_tokens():
    assert is_safe_input(_request(occasion="путин на юбилее")) is False
    assert is_safe_input(_request(target="фашист")) is False
    assert is_safe_input(_request(facts=["жид да чурка"])) is False


# --- вывод ---------------------------------------------------------------


def test_safe_text_passes_clean_chastushka():
    assert is_safe_text("Мы споём вам без прикрас\nПро Ивана юбилей") is True


def test_safe_text_blocks_blocked_token_with_punctuation():
    assert is_safe_text("А потом он крикнул: ебать!") is False


def test_safe_text_is_case_insensitive():
    assert is_safe_text("ПИЗДА как пизда") is False


# --- зажатие boldness в safe-режиме --------------------------------------


def test_safe_boldness_clamps_in_safe_mode():
    assert safe_boldness(5, safe_mode=True) == 3
    assert safe_boldness(4, safe_mode=True) == 3
    assert safe_boldness(2, safe_mode=True) == 2


def test_safe_boldness_preserves_outside_safe_mode():
    assert safe_boldness(5, safe_mode=False) == 5
    assert safe_boldness(0, safe_mode=False) == 0


# --- фильтрация небезопасных кандидатов в pipeline -----------------------

from app.services.pipeline import generate_pack  # noqa: E402

SAFE_LINES = [
    "Мы споём вам без прикрас,",
    "Про Ивана юбилей,",
    "Вот вам факт под номер раз:",
    "Рыбалка — и весь рай!",
]
UNSAFE_LINES = [
    "А потом он крикнул: ебать,",
    "Как же я люблю рыбалку,",
    "Пиши частушки, не догнать,",
    "Хуй с ним, пойду гулять.",
]


class _OneUnsafeLLM(ChastushkaLLM):
    """Три кандидата: два безопасных, один с ненормативной лексикой."""

    def generate(self, request, suffix=""):
        return [SAFE_LINES, UNSAFE_LINES, SAFE_LINES]


def test_generate_pack_drops_unsafe_candidates_in_safe_mode():
    pack = generate_pack(_request(count=3), llm=_OneUnsafeLLM())
    texts = "\n".join(c.text for c in pack.candidates)
    assert "ебать" not in texts
    assert "Хуй" not in texts
    assert len(pack.candidates) == 2
    assert all(c.safe for c in pack.candidates)


def test_generate_pack_keeps_unsafe_candidates_outside_safe_mode():
    request = _request(safe_mode=False, boldness=5, count=3)
    pack = generate_pack(request, llm=_OneUnsafeLLM())
    assert len(pack.candidates) == 3  # небезопасный не режется вне safe-режима


class _AllUnsafeLLM(ChastushkaLLM):
    def generate(self, request, suffix=""):
        return [UNSAFE_LINES, UNSAFE_LINES, UNSAFE_LINES]


def test_generate_pack_raises_when_all_candidates_unsafe_in_safe_mode():
    with pytest.raises(ModerationError):
        generate_pack(_request(count=3), llm=_AllUnsafeLLM())