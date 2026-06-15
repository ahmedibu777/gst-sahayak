import os
from unittest.mock import patch, MagicMock

import pytest

from utils.llm_providers import (
    build_user_message,
    get_available_providers,
    resolve_provider,
    chat_completion,
    llm_fallback,
    PROVIDER_CONFIG,
)


def test_build_user_message():
    msg = build_user_message("What is ITC?", "GST context", {"state": "Karnataka"})
    assert "What is ITC?" in msg
    assert "GST context" in msg
    assert "Karnataka" in msg


def test_get_available_providers_none():
    with patch.dict(os.environ, {}, clear=True):
        assert get_available_providers() == []


def test_get_available_providers_openai():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=True):
        assert "openai" in get_available_providers()


def test_resolve_provider_auto_picks_first():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "g-test"}, clear=True):
        assert resolve_provider("auto") == "gemini"


def test_resolve_provider_explicit():
    with patch.dict(
        os.environ,
        {"OPENAI_API_KEY": "sk-o", "GEMINI_API_KEY": "g-test"},
        clear=True,
    ):
        assert resolve_provider("openai") == "openai"


def test_resolve_provider_missing_key():
    with patch.dict(os.environ, {}, clear=True):
        assert resolve_provider("claude") is None


@patch("utils.llm_providers.requests.post")
def test_chat_completion_openai(mock_post):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"choices": [{"message": {"content": "Test answer"}}]}
    mock_resp.raise_for_status = MagicMock()
    mock_post.return_value = mock_resp

    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=True):
        result = chat_completion("openai", "Hello")
        assert result == "Test answer"
        assert "api.openai.com" in mock_post.call_args[0][0]


@patch("utils.llm_providers.chat_completion")
def test_llm_fallback_success(mock_chat):
    mock_chat.return_value = "GST guidance here"
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test"}, clear=True):
        result = llm_fallback("query", "ctx", {"state": "Delhi"}, provider="openai", disclaimer_fn=lambda: " [D]")
        assert "OpenAI response" in result
        assert "GST guidance here" in result
        assert result.endswith(" [D]")


def test_llm_fallback_no_key():
    with patch.dict(os.environ, {}, clear=True):
        result = llm_fallback("query", "local ctx", disclaimer_fn=lambda: " [D]")
        assert "No LLM API key configured" in result
        assert "local ctx" in result