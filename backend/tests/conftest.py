"""Общие фикстуры тестов.

Контрактные тесты бьют по реальному FastAPI-приложению, поэтому LLM подменяется
детерминированной заглушкой — без сетевых вызовов и без ANTHROPIC_API_KEY.
"""

import pytest

from app.main import app
from app.schemas import GeneratePackRequest
from app.services.llm import ChastushkaLLM, get_llm


class StubLLM(ChastushkaLLM):
    """Заглушка LLM: возвращает ровно `count` детерминированных частушек."""

    def generate(self, request: GeneratePackRequest, suffix: str = "") -> list[list[str]]:
        facts = request.facts or ["просто так"]
        chastushki: list[list[str]] = []
        for index in range(request.count):
            fact = facts[index % len(facts)]
            chastushki.append(
                [
                    "Мы споём вам без прикрас,",
                    f"Про {request.target} на {request.occasion},",
                    f"Вот вам факт под номер {index + 1}:",
                    f"{fact} — и весь сказ!",
                ],
            )
        return chastushki


@pytest.fixture(autouse=True)
def stub_llm():
    """Подменяет LLM-зависимость заглушкой на время каждого теста."""
    app.dependency_overrides[get_llm] = lambda: StubLLM()
    yield
    app.dependency_overrides.pop(get_llm, None)
