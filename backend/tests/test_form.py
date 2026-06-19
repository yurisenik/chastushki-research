"""Тесты слоя проверки частушечной формы (инкремент 2).

Эвристики без внешних словарей: слоги по гласным, рифмовое ядро по открытости
последнего слога, структура AABB/ABCB. Тесты фиксируют именно дискриминацию
хорошей и плохой формы — точность лингвистики сознательно упрощена (Фаза 2).
"""

from app.services.form import (
    count_syllables,
    rhyme_core,
    rhymes,
    rhythm_score,
    rhyme_score,
    score_candidate,
)


# --- слоги ---------------------------------------------------------------


def test_count_syllables_by_vowels():
    assert count_syllables("ааа") == 3
    assert count_syllables("кот") == 1
    assert count_syllables("малина") == 3
    assert count_syllables("подъезд") == 2  # ъ/ь — не гласные
    assert count_syllables("") == 0
    assert count_syllables("Ёлка") == 2  # ё — одна гласная, регистр не важен


# --- рифмовое ядро и рифма -----------------------------------------------


def test_rhyme_core_feminine_captures_two_syllables():
    # открытый последний слог → ядро от предпоследней гласной
    assert rhyme_core("малина") == "ина"
    assert rhyme_core("долина") == "ина"


def test_rhyme_core_masculine_captures_last_syllable():
    # последний слог закрыт согласной → ядро от последней гласной
    assert rhyme_core("глаз") == "аз"
    assert rhyme_core("раз") == "аз"


def test_rhymes_detects_matching_cores():
    assert rhymes("малина", "долина") is True
    assert rhymes("глаз", "раз") is True
    assert rhymes("кот", "лот") is True


def test_rhymes_rejects_different_stress_or_core():
    # односложное ядро совпадает по последней гласной, но ударение/ядро разные
    assert rhymes("малина", "собака") is False  # "ина" vs "ака"
    assert rhymes("кот", "пёс") is False  # "от" vs "ёс"->"ес"
    assert rhymes("хлеб", "кот") is False  # "еб" vs "от"
    # с/з — звонкая/глухая пара; MVP-эвристика их не схлопывает
    assert rhymes("глаз", "нас") is False  # "аз" vs "ас"


def test_rhymes_strips_punctuation_and_case():
    assert rhymes("Глаз,", "раз!") is True
    assert rhymes("МАЛИНА", "долина") is True


# --- ритм и структура ----------------------------------------------------


GOOD_AABB = (
    "На крылечке спал рыжий кот\n"
    "Во дворе большом гулял пёс\n"
    "А на лавочке лежал лот\n"
    "И залаял на утёс"
)

BAD_FORM = "кот\nсобака\nхлеб\nтракторизм"


def test_rhythm_score_rewards_lines_in_window():
    # все 4 строки в окне 7..10 слогов
    lines = GOOD_AABB.split("\n")
    assert rhythm_score(lines) == 1.0


def test_rhythm_score_penalizes_out_of_window():
    lines = BAD_FORM.split("\n")
    assert rhythm_score(lines) == 0.0


def test_rhyme_score_aabb_is_full():
    lines = GOOD_AABB.split("\n")
    # 1-3 рифмуются (кот/лот) и 2-4 рифмуются (пёс/утёс) -> AABB
    assert rhyme_score(lines) == 1.0


def test_rhyme_score_abcb_partial():
    # только 2-4 рифмуются -> 0.6
    abcb = "На крылечке спал рыжий кот\nВо дворе большом гулял пёс\nА на лавке дремлет котёнок\nИ залаял на утёс"
    lines = abcb.split("\n")
    # 1-3: кот/котёнок -> "от" vs "ок"? нет; 2-4: пёс/утёс -> да
    assert rhyme_score(lines) == 0.6


def test_rhyme_score_no_rhyme_is_zero():
    lines = BAD_FORM.split("\n")
    assert rhyme_score(lines) == 0.0


# --- composite score -----------------------------------------------------


def test_score_candidate_rewards_good_form():
    assert score_candidate(GOOD_AABB) == 1.0


def test_score_candidate_punishes_bad_form():
    assert score_candidate(BAD_FORM) == 0.0


def test_score_candidate_zero_for_wrong_line_count():
    assert score_candidate("одна строка") == 0.0
    assert score_candidate("а\nб\nв") == 0.0


def test_good_form_outscores_bad_form():
    assert score_candidate(GOOD_AABB) > score_candidate(BAD_FORM)


# --- ранжирование в pipeline (инкремент 2, Этап D) ------------------------

from app.schemas import GeneratePackRequest  # noqa: E402
from app.services.llm import ChastushkaLLM  # noqa: E402
from app.services.pipeline import generate_pack  # noqa: E402


class _MixedQualityLLM(ChastushkaLLM):
    """Два хороших (AABB) и один плохой (нет формы) кандидат."""

    def generate(self, request, suffix=""):
        return [GOOD_AABB.split("\n"), BAD_FORM.split("\n"), GOOD_AABB.split("\n")]


def test_generate_pack_ranks_good_form_first():
    request = GeneratePackRequest(
        occasion="праздник",
        target="гости",
        facts=[],
        tone="funny",
        boldness=2,
        safe_mode=True,
        count=3,
    )
    pack = generate_pack(request, llm=_MixedQualityLLM())

    assert pack.candidates[0].text == GOOD_AABB
    assert pack.candidates[0].score > pack.candidates[-1].score
    # плохая форма тонет на дно
    assert pack.candidates[-1].text == BAD_FORM
    assert pack.candidates[-1].score == 0.0