"""Общие фикстуры тестов.

Контрактные тесты бьют по реальному FastAPI-приложению, поэтому LLM подменяется
детерминированной заглушкой — без сетевых вызовов и без ANTHROPIC_API_KEY.
"""

import pytest

from app.main import app
from app.schemas import GeneratePackRequest
from app.services.llm import ChastushkaLLM, get_llm
from app.services.store import InMemoryPackStore, get_store


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
    """Подменяет LLM- и store-зависимости на время каждого теста.

    Store — один in-memory инстанс на тест (общий для всех запросов теста),
    чтобы контрактные тесты оставались детерминированными и не зависели от БД
    (даже если в окружении задан DATABASE_URL, как в CI).
    """
    store = InMemoryPackStore()
    app.dependency_overrides[get_llm] = lambda: StubLLM()
    app.dependency_overrides[get_store] = lambda: store
    yield
    app.dependency_overrides.pop(get_llm, None)
    app.dependency_overrides.pop(get_store, None)
