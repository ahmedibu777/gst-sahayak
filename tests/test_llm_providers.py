import os
from unittest.mock import patch, MagicMock

from utils.llm_providers import (
    build_user_message,
    get_available_providers,
    get_provider_status,
    resolve_provider,
    chat_completion,
    llm_fallback,
    PROVIDER_CONFIG,
    PROVIDER_PRIORITY,
)


def test_all_providers_have_required_fields():
    for pid, cfg in PROVIDER_CONFIG.items():
        assert "label" in cfg
        assert "type" in cfg
        assert pid in PROVIDER_PRIORITY


def test_build_user_message():
    msg = build_user_message("What is ITC?", "GST context", {"state": "Karnataka"})
    assert "What is ITC?" in msg
    assert "Karnataka" in msg


def test_get_available_providers_none():
    with patch.dict(os.environ, {}, clear=True):
        assert get_available_providers() == []


def test_get_available_providers_multiple():
    with patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "sk-real", "GEMINI_API_KEY": "g-real"},
        clear=True,
    ):
        available = get_available_providers()
        assert "openai" in available
        assert "gemini" in available


def test_placeholder_keys_ignored():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "your_openai_api_key_here"}, clear=True):
        assert "openai" not in get_available_providers()


def test_resolve_provider_auto_picks_first_available():
    with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "ds-key"}, clear=True):
        assert resolve_provider("auto") == "deepseek"


def test_resolve_provider_explicit():
    with patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "sk-o", "GEMINI_API_KEY": "g-test"},
        clear=True,
    ):
        assert resolve_provider("openai") == "openai"


def test_get_provider_status_counts():
    with patch.dict(os.environ, {"GROQ_API_KEY": "gq-key"}, clear=True):
        status = get_provider_status()
        configured = [s for s in status if s["configured"]]
        assert len(configured) == 1
        assert configured[0]["id"] == "groq"


@patch("utils.llm_providers.requests.post")
def test_chat_completion_openai(mock_post):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"choices": [{"message": {"content": "Test answer"}}]}
    mock_resp.raise_for_status = MagicMock()
    mock_post.return_value = mock_resp

    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=True):
        result = chat_completion("openai", "Hello")
        assert result == "Test answer"


@patch("utils.llm_providers.chat_completion")
def test_llm_fallback_success(mock_chat):
    mock_chat.return_value = "GST guidance"
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=True):
        result = llm_fallback("query", "ctx", provider="openai", disclaimer_fn=lambda: " [D]")
        assert "OpenAI response" in result
        assert result.endswith(" [D]")


@patch("utils.llm_providers.chat_completion")
def test_llm_fallback_auto_tries_next_on_failure(mock_chat):
    mock_chat.side_effect = [Exception("fail"), "Recovered answer"]
    with patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "sk-o", "GEMINI_API_KEY": "g-key"},
        clear=True,
    ):
        result = llm_fallback("query", "ctx", provider="auto", disclaimer_fn=lambda: "")
        assert mock_chat.call_count == 2
        assert "Recovered answer" in result


def test_llm_fallback_no_key():
    with patch.dict(os.environ, {}, clear=True):
        result = llm_fallback("query", "local ctx", disclaimer_fn=lambda: " [D]")
        assert "No LLM API key configured" in result