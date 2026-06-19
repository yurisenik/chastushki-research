"""Тесты двухпроходной генерации LLM-провайдеров с замоканными клиентами."""

import json

import pytest

from app.schemas import GeneratePackRequest
from app.services.llm import (
    ClaudeChastushkaLLM,
    LLMError,
    OpenAIChastushkaLLM,
    get_llm,
)


class _Block:
    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text


class _Response:
    def __init__(self, text: str) -> None:
        self.content = [_Block(text)]


class _Messages:
    """Мок `client.messages`: отдаёт заранее заданные ответы по очереди."""

    def __init__(self, outputs: list) -> None:
        self._outputs = list(outputs)
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if not self._outputs:
            raise AssertionError("неожиданный лишний вызов Claude")
        result = self._outputs.pop(0)
        if isinstance(result, Exception):
            raise result
        return _Response(result)


class _FakeClient:
    def __init__(self, outputs: list) -> None:
        self.messages = _Messages(outputs)


def _request(count: int = 4) -> GeneratePackRequest:
    return GeneratePackRequest(
        occasion="юбилей",
        target="Иван",
        facts=["любит рыбалку"],
        tone="funny",
        boldness=2,
        safe_mode=True,
        count=count,
    )


def _plan_json(count: int) -> str:
    plans = [{"theme": "t", "image": "i", "joke": "j", "rhyme": "r"} for _ in range(count)]
    return json.dumps(plans, ensure_ascii=False)


def _lines_json(count: int) -> str:
    items = [{"lines": ["раз", "два", "три", "четыре"]} for _ in range(count)]
    return json.dumps(items, ensure_ascii=False)


def test_generate_runs_two_passes_and_returns_chastushki():
    client = _FakeClient([_plan_json(4), _lines_json(4)])
    llm = ClaudeChastushkaLLM(client=client)

    result = llm.generate(_request(4))

    assert len(client.messages.calls) == 2
    assert len(result) == 4
    assert all(len(lines) == 4 for lines in result)


def test_plan_pass_precedes_lines_pass():
    client = _FakeClient([_plan_json(3), _lines_json(3)])
    llm = ClaudeChastushkaLLM(client=client)

    llm.generate(_request(3))

    plan_prompt = client.messages.calls[0]["messages"][0]["content"]
    lines_prompt = client.messages.calls[1]["messages"][0]["content"]
    assert "план" in plan_prompt.lower()
    assert "lines" in lines_prompt


def test_system_prompt_is_stable_and_cached():
    client = _FakeClient([_plan_json(3), _lines_json(3)])
    llm = ClaudeChastushkaLLM(client=client)

    llm.generate(_request(3))

    system_first = client.messages.calls[0]["system"]
    system_second = client.messages.calls[1]["system"]
    assert system_first == system_second
    assert system_first[-1]["cache_control"] == {"type": "ephemeral"}


def test_parses_json_wrapped_in_markdown_fence():
    fenced_plan = f"```json\n{_plan_json(3)}\n```"
    client = _FakeClient([fenced_plan, _lines_json(3)])
    llm = ClaudeChastushkaLLM(client=client)

    result = llm.generate(_request(3))

    assert len(result) == 3


def test_llm_error_on_transport_failure():
    client = _FakeClient([RuntimeError("network down")])
    llm = ClaudeChastushkaLLM(client=client)

    with pytest.raises(LLMError):
        llm.generate(_request(3))


def test_llm_error_on_invalid_json():
    client = _FakeClient(["в ответе нет никакого JSON", _lines_json(3)])
    llm = ClaudeChastushkaLLM(client=client)

    with pytest.raises(LLMError):
        llm.generate(_request(3))


# --- OpenAI: мок клиента Chat Completions ---------------------------------


class _OAMessage:
    def __init__(self, content: str | None) -> None:
        self.content = content


class _OAChoice:
    def __init__(self, content: str | None) -> None:
        self.message = _OAMessage(content)


class _OAResponse:
    def __init__(self, content: str | None) -> None:
        self.choices = [_OAChoice(content)]


class _OACompletions:
    def __init__(self, outputs: list) -> None:
        self._outputs = list(outputs)
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if not self._outputs:
            raise AssertionError("неожиданный лишний вызов OpenAI")
        result = self._outputs.pop(0)
        if isinstance(result, Exception):
            raise result
        return _OAResponse(result)


class _FakeOpenAIClient:
    def __init__(self, outputs: list) -> None:
        self.chat = type("_Chat", (), {"completions": _OACompletions(outputs)})()


def test_openai_runs_two_passes_and_returns_chastushki():
    client = _FakeOpenAIClient([_plan_json(4), _lines_json(4)])
    llm = OpenAIChastushkaLLM(client=client, model="gpt-4o")

    result = llm.generate(_request(4))

    assert len(client.chat.completions.calls) == 2
    assert len(result) == 4
    assert all(len(lines) == 4 for lines in result)


def test_openai_sends_system_and_user_messages():
    client = _FakeOpenAIClient([_plan_json(3), _lines_json(3)])
    llm = OpenAIChastushkaLLM(client=client, model="gpt-4o")

    llm.generate(_request(3))

    call = client.chat.completions.calls[0]
    assert call["model"] == "gpt-4o"
    assert [m["role"] for m in call["messages"]] == ["system", "user"]


def test_openai_llm_error_on_transport_failure():
    client = _FakeOpenAIClient([RuntimeError("network down")])
    llm = OpenAIChastushkaLLM(client=client, model="gpt-4o")

    with pytest.raises(LLMError):
        llm.generate(_request(3))


def test_openai_llm_error_on_empty_response():
    client = _FakeOpenAIClient([None])
    llm = OpenAIChastushkaLLM(client=client, model="gpt-4o")

    with pytest.raises(LLMError):
        llm.generate(_request(3))


def test_get_llm_selects_provider_from_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    get_llm.cache_clear()
    assert isinstance(get_llm(), OpenAIChastushkaLLM)

    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    get_llm.cache_clear()
    assert isinstance(get_llm(), ClaudeChastushkaLLM)

    get_llm.cache_clear()
