"""LLM-слой генерации частушек.

Двухпроходная генерация (план → строки) реализована один раз в `_TwoPassLLM`;
конкретный провайдер задаёт только `_complete()` — один запрос к своему API.

Провайдеры:
  - `ClaudeChastushkaLLM`  — Anthropic Claude API (prompt caching через cache_control);
  - `OpenAIChastushkaLLM`  — OpenAI Chat Completions API (кэширование промпта серверное).

Активный провайдер выбирается переменной окружения `LLM_PROVIDER`
(`openai` по умолчанию, либо `anthropic`).
"""

import abc
import json
import os
from functools import lru_cache

import anthropic
import openai

from app.prompts import SYSTEM_PROMPT, build_lines_prompt, build_plan_prompt
from app.schemas import GeneratePackRequest


CLAUDE_MODEL = "claude-opus-4-7"
DEFAULT_OPENAI_MODEL = "gpt-4o"
MAX_TOKENS = 16000

# Claude: системный промпт уходит отдельным стабильным блоком с точкой кэширования.
SYSTEM_BLOCKS = [
    {
        "type": "text",
        "text": SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"},
    },
]


class LLMError(RuntimeError):
    """Сбой генерации: ошибка API или невалидный ответ модели."""


def _extract_json_array(text: str) -> list:
    """Достать JSON-массив из ответа модели (терпимо к markdown-ограждению)."""
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise LLMError("модель не вернула JSON-массив")
    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise LLMError("модель вернула невалидный JSON") from exc
    if not isinstance(data, list):
        raise LLMError("корень JSON-ответа не является массивом")
    return data


class ChastushkaLLM(abc.ABC):
    """Интерфейс генератора частушек (позволяет подменять реализацию в тестах)."""

    @abc.abstractmethod
    def generate(self, request: GeneratePackRequest, suffix: str = "") -> list[list[str]]:
        """Вернуть список частушек; каждая частушка — список строк."""


class _TwoPassLLM(ChastushkaLLM):
    """Двухпроходная генерация поверх провайдер-зависимого `_complete()`."""

    @abc.abstractmethod
    def _complete(self, user_prompt: str) -> str:
        """Один запрос к модели: системный промпт + user-сообщение -> текст ответа."""

    def generate(self, request: GeneratePackRequest, suffix: str = "") -> list[list[str]]:
        # Проход 1: планы.
        plans = _extract_json_array(self._complete(build_plan_prompt(request, suffix)))

        # Проход 2: готовые строки по планам.
        plans_json = json.dumps(plans, ensure_ascii=False)
        items = _extract_json_array(
            self._complete(build_lines_prompt(request, plans_json, suffix))
        )

        chastushki: list[list[str]] = []
        for item in items:
            lines = item.get("lines") if isinstance(item, dict) else item
            if not isinstance(lines, list) or not lines:
                raise LLMError("в ответе есть частушка без строк")
            chastushki.append([str(line) for line in lines])
        return chastushki


class ClaudeChastushkaLLM(_TwoPassLLM):
    """Генерация частушек через Claude API (Anthropic)."""

    def __init__(self, client: anthropic.Anthropic | None = None) -> None:
        # Клиент создаётся лениво: импорт модуля не требует ANTHROPIC_API_KEY.
        self._client = client

    def _ensure_client(self) -> anthropic.Anthropic:
        if self._client is None:
            self._client = anthropic.Anthropic()
        return self._client

    def _complete(self, user_prompt: str) -> str:
        try:
            response = self._ensure_client().messages.create(
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS,
                thinking={"type": "adaptive"},
                system=SYSTEM_BLOCKS,
                messages=[{"role": "user", "content": user_prompt}],
            )
        except Exception as exc:  # любой сбой SDK/сети -> доменная ошибка
            raise LLMError(f"запрос к Claude не удался: {exc}") from exc

        parts = [
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text"
        ]
        if not parts:
            raise LLMError("ответ Claude не содержит текста")
        return "".join(parts)


class OpenAIChastushkaLLM(_TwoPassLLM):
    """Генерация частушек через OpenAI Chat Completions API."""

    def __init__(
        self,
        client: openai.OpenAI | None = None,
        model: str | None = None,
    ) -> None:
        # Клиент создаётся лениво: импорт модуля не требует OPENAI_API_KEY.
        self._client = client
        self._model = model or os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)

    def _ensure_client(self) -> openai.OpenAI:
        if self._client is None:
            self._client = openai.OpenAI()
        return self._client

    def _complete(self, user_prompt: str) -> str:
        try:
            response = self._ensure_client().chat.completions.create(
                model=self._model,
                max_completion_tokens=MAX_TOKENS,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except Exception as exc:  # любой сбой SDK/сети -> доменная ошибка
            raise LLMError(f"запрос к OpenAI не удался: {exc}") from exc

        choices = getattr(response, "choices", None) or []
        content = choices[0].message.content if choices else None
        if not content:
            raise LLMError("ответ OpenAI не содержит текста")
        return content


@lru_cache(maxsize=1)
def get_llm() -> ChastushkaLLM:
    """FastAPI-зависимость: активный провайдер LLM (подменяется в тестах).

    Выбор провайдера — переменная окружения `LLM_PROVIDER`:
    `openai` (по умолчанию) или `anthropic`/`claude`.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    if provider in {"openai", "gpt"}:
        return OpenAIChastushkaLLM()
    if provider in {"anthropic", "claude"}:
        return ClaudeChastushkaLLM()
    raise LLMError(f"неизвестный LLM_PROVIDER: {provider!r}")
