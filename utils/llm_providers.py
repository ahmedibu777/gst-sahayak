"""
Multi-provider LLM fallback for GST Sahayak.
Supports: Grok, OpenAI, Gemini, Claude, Hugging Face.
"""

import os
import requests
from typing import Optional

SYSTEM_PROMPT = (
    "You are GST Sahayak, an empathetic, accurate GST compliance assistant for Indian small businesses, "
    "freelancers and CA students. Use ONLY verified knowledge from context. "
    "Be helpful, clear, and use simple language. Always end with the disclaimer."
)

PROVIDER_CONFIG = {
    "grok": {
        "env_key": "GROK_API_KEY",
        "model_env": "GROK_MODEL",
        "default_model": "grok-beta",
        "label": "Grok (x.ai)",
    },
    "openai": {
        "env_key": "OPENAI_API_KEY",
        "model_env": "OPENAI_MODEL",
        "default_model": "gpt-4o-mini",
        "label": "OpenAI",
    },
    "gemini": {
        "env_key": "GEMINI_API_KEY",
        "model_env": "GEMINI_MODEL",
        "default_model": "gemini-2.0-flash",
        "label": "Google Gemini",
    },
    "claude": {
        "env_key": "ANTHROPIC_API_KEY",
        "model_env": "CLAUDE_MODEL",
        "default_model": "claude-3-5-haiku-latest",
        "label": "Anthropic Claude",
    },
    "huggingface": {
        "env_key": "HF_TOKEN",
        "model_env": "HF_MODEL",
        "default_model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "label": "Hugging Face",
    },
}

PROVIDER_PRIORITY = ["grok", "openai", "gemini", "claude", "huggingface"]
REQUEST_TIMEOUT = 25


def _get_api_key(provider: str) -> Optional[str]:
    env_key = PROVIDER_CONFIG[provider]["env_key"]
    value = os.getenv(env_key, "").strip()
    return value or None


def _get_model(provider: str) -> str:
    cfg = PROVIDER_CONFIG[provider]
    return os.getenv(cfg["model_env"], cfg["default_model"]).strip()


def get_available_providers() -> list[str]:
    """Return provider ids that have API keys configured."""
    return [p for p in PROVIDER_PRIORITY if _get_api_key(p)]


def resolve_provider(preferred: Optional[str] = None) -> Optional[str]:
    """Pick provider: explicit choice, LLM_PROVIDER env, or first available key."""
    if preferred and preferred != "auto" and preferred in PROVIDER_CONFIG:
        if _get_api_key(preferred):
            return preferred
        return None

    env_provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    if env_provider and env_provider != "auto" and env_provider in PROVIDER_CONFIG:
        if _get_api_key(env_provider):
            return env_provider

    available = get_available_providers()
    return available[0] if available else None


def build_user_message(query: str, context: str, user_profile: dict) -> str:
    return f"Context: {context}\n\nUser Query: {query}\n\nUser Profile: {user_profile}"


def _chat_openai_compatible(url: str, api_key: str, model: str, user_message: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.3,
        "max_tokens": 800,
    }
    response = requests.post(
        url,
        json=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _chat_grok(api_key: str, model: str, user_message: str) -> str:
    return _chat_openai_compatible(
        "https://api.x.ai/v1/chat/completions", api_key, model, user_message
    )


def _chat_openai(api_key: str, model: str, user_message: str) -> str:
    return _chat_openai_compatible(
        "https://api.openai.com/v1/chat/completions", api_key, model, user_message
    )


def _chat_huggingface(api_key: str, model: str, user_message: str) -> str:
    return _chat_openai_compatible(
        "https://router.huggingface.co/v1/chat/completions", api_key, model, user_message
    )


def _chat_gemini(api_key: str, model: str, user_message: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_message}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 800},
    }
    response = requests.post(
        url,
        params={"key": api_key},
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def _chat_claude(api_key: str, model: str, user_message: str) -> str:
    payload = {
        "model": model,
        "max_tokens": 800,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_message}],
    }
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        json=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["content"][0]["text"]


_CHAT_HANDLERS = {
    "grok": _chat_grok,
    "openai": _chat_openai,
    "gemini": _chat_gemini,
    "claude": _chat_claude,
    "huggingface": _chat_huggingface,
}


def chat_completion(provider: str, user_message: str) -> str:
    """Call the selected LLM provider and return raw response text."""
    api_key = _get_api_key(provider)
    if not api_key:
        raise ValueError(f"No API key for provider: {provider}")

    model = _get_model(provider)
    handler = _CHAT_HANDLERS[provider]
    return handler(api_key, model, user_message)


def llm_fallback(
    query: str,
    context: str = "",
    user_profile: Optional[dict] = None,
    provider: Optional[str] = None,
    disclaimer_fn=None,
) -> str:
    """
    Route complex queries to the configured LLM provider.
    Falls back to local context if no API key is set or the call fails.
    """
    if disclaimer_fn is None:
        from utils.disclaimers import get_disclaimer
        disclaimer_fn = get_disclaimer

    user_profile = user_profile or {}
    user_message = build_user_message(query, context, user_profile)
    resolved = resolve_provider(provider)

    if not resolved:
        available_labels = [PROVIDER_CONFIG[p]["label"] for p in PROVIDER_PRIORITY]
        return (
            "⚠️ No LLM API key configured. Add one of these to `.env`:\n"
            + "\n".join(f"• {label}" for label in available_labels)
            + f"\n\nHere's what I know locally: {context}"
            + disclaimer_fn()
        )

    try:
        content = chat_completion(resolved, user_message)
        label = PROVIDER_CONFIG[resolved]["label"]
        return f"_{label} response_\n\n{content}" + disclaimer_fn()
    except Exception:
        return (
            f"Sorry, I had trouble connecting to {PROVIDER_CONFIG[resolved]['label']}. "
            f"Here's what I know locally: {context}"
            + disclaimer_fn()
        )


def provider_label(provider_id: str) -> str:
    return PROVIDER_CONFIG.get(provider_id, {}).get("label", provider_id)