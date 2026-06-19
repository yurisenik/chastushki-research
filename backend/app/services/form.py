"""Формальная проверка частушечной формы (инкремент 2, Этап C техплана).

MVP-эвристики без внешних словарей (pymorphy2/rupo отложены в Фазу 2 —
`08_implementation_plan.md` §6, `02_technical_plan.md` §17). Точность
сознательно упрощена: цель — дискриминация хорошей и плохой формы для
ранжирования, а не лингвистически безупречная разметка.

- Слоги считаются по гласным (аеёиоуыэюя, ё — одна гласная).
- Рифмовое ядро — от ударной гласной до конца; приближается эвристикой по
  открытости последнего слога: закрытый согласной -> одна гласная (мужская),
  открытый (оканчивается на гласную) -> две гласные (женская).
- Структура AABB (1-3 и 2-4 рифмуются) или ABCB (только 2-4).
"""

import re

VOWELS = set("аеёиоуыэюя")
MIN_SYLLABLES = 7
MAX_SYLLABLES = 10

_WORD_RE = re.compile(r"[а-яё]+", re.IGNORECASE)


def count_syllables(line: str) -> int:
    """Количество слогов в строке — по числу гласных."""
    return sum(1 for ch in line.lower() if ch in VOWELS)


def _last_word(line: str) -> str:
    match = _WORD_RE.findall(line)
    return match[-1].lower() if match else ""


def rhyme_core(word: str) -> str:
    """Рифмовое ядро слова: от ударной гласной до конца (эвристика).

    ё нормализуется в е (орфографически часто взаимозаменяемы). Последний слог,
    закрытый согласной, даёт односложное ядро; открытый (на гласную) —
    двусложное (захватываем предпоследнюю гласную, т.к. ударение обычно
    раньше).
    """
    word = word.lower().replace("ё", "е")
    vowel_indices = [i for i, ch in enumerate(word) if ch in VOWELS]
    if not vowel_indices:
        return word
    last = vowel_indices[-1]
    if word[-1] in VOWELS and len(vowel_indices) >= 2:
        # открытый последний слог — ядро от предпоследней гласной
        return word[vowel_indices[-2]:]
    return word[last:]


def rhymes(line_a: str, line_b: str) -> bool:
    """Рифмуются ли строки (по рифмовому ядру последних слов)."""
    return rhyme_core(_last_word(line_a)) == rhyme_core(_last_word(line_b))


def rhythm_score(lines: list[str]) -> float:
    """Доля строк, попавших в частушечное слоговое окно 7..10."""
    if not lines:
        return 0.0
    in_window = sum(
        1 for line in lines if MIN_SYLLABLES <= count_syllables(line) <= MAX_SYLLABLES
    )
    return in_window / len(lines)


def rhyme_score(lines: list[str]) -> float:
    """Оценка рифмованной структуры: 2-4 обязательны (0.6), 1-3 — бонус (0.4).

    AABB -> 1.0, ABCB -> 0.6, нет рифмы -> 0.0.
    """
    if len(lines) < 4:
        return 0.0
    r24 = 1.0 if rhymes(lines[1], lines[3]) else 0.0
    r13 = 1.0 if rhymes(lines[0], lines[2]) else 0.0
    return round(0.6 * r24 + 0.4 * r13, 3)


def score_candidate(text: str) -> float:
    """Composite-оценка кандидата по форме: 0.5*ритм + 0.5*рифма, 0..1.

    Не 4 строки -> 0.0 (структурный провал). topic/style/safety из формулы
    техплана §D здесь не считаются — они закрываются в других инкрементах.
    """
    lines = [line for line in text.split("\n") if line.strip()]
    if len(lines) != 4:
        return 0.0
    return round(0.5 * rhythm_score(lines) + 0.5 * rhyme_score(lines), 3)