"""
Multi-provider LLM fallback for GST Sahayak.
Users can configure one, several, or all providers via .env keys.
"""

import os
import requests
from typing import Callable, Optional

SYSTEM_PROMPT = (
    "You are GST Sahayak, an empathetic, accurate GST compliance assistant for Indian small businesses, "
    "freelancers and CA students. Use ONLY verified knowledge from context. "
    "Be helpful, clear, and use simple language. Always end with the disclaimer."
)

REQUEST_TIMEOUT = 25

# type: openai | gemini | claude | cohere | azure | ollama
PROVIDER_CONFIG: dict[str, dict] = {
    "openrouter": {
        "label": "OpenRouter",
        "type": "openai",
        "env_key": "OPENROUTER_API_KEY",
        "model_env": "OPENROUTER_MODEL",
        "default_model": "openai/gpt-4o-mini",
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "extra_headers": {"HTTP-Referer": "https://github.com/ahmedibu777/gst-sahayak", "X-Title": "GST Sahayak"},
    },
    "openai": {
        "label": "OpenAI",
        "type": "openai",
        "env_key": "OPENAI_API_KEY",
        "model_env": "OPENAI_MODEL",
        "default_model": "gpt-4o-mini",
        "base_url": "https://api.openai.com/v1/chat/completions",
    },
    "gemini": {
        "label": "Google Gemini",
        "type": "gemini",
        "env_key": "GEMINI_API_KEY",
        "model_env": "GEMINI_MODEL",
        "default_model": "gemini-2.0-flash",
    },
    "groq": {
        "label": "Groq",
        "type": "openai",
        "env_key": "GROQ_API_KEY",
        "model_env": "GROQ_MODEL",
        "default_model": "llama-3.3-70b-versatile",
        "base_url": "https://api.groq.com/openai/v1/chat/completions",
    },
    "deepseek": {
        "label": "DeepSeek",
        "type": "openai",
        "env_key": "DEEPSEEK_API_KEY",
        "model_env": "DEEPSEEK_MODEL",
        "default_model": "deepseek-chat",
        "base_url": "https://api.deepseek.com/v1/chat/completions",
    },
    "claude": {
        "label": "Anthropic Claude",
        "type": "claude",
        "env_key": "ANTHROPIC_API_KEY",
        "model_env": "CLAUDE_MODEL",
        "default_model": "claude-3-5-haiku-latest",
    },
    "grok": {
        "label": "Grok (x.ai)",
        "type": "openai",
        "env_key": "GROK_API_KEY",
        "model_env": "GROK_MODEL",
        "default_model": "grok-beta",
        "base_url": "https://api.x.ai/v1/chat/completions",
    },
    "mistral": {
        "label": "Mistral AI",
        "type": "openai",
        "env_key": "MISTRAL_API_KEY",
        "model_env": "MISTRAL_MODEL",
        "default_model": "mistral-small-latest",
        "base_url": "https://api.mistral.ai/v1/chat/completions",
    },
    "together": {
        "label": "Together AI",
        "type": "openai",
        "env_key": "TOGETHER_API_KEY",
        "model_env": "TOGETHER_MODEL",
        "default_model": "meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
        "base_url": "https://api.together.xyz/v1/chat/completions",
    },
    "huggingface": {
        "label": "Hugging Face",
        "type": "openai",
        "env_key": "HF_TOKEN",
        "model_env": "HF_MODEL",
        "default_model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "base_url": "https://router.huggingface.co/v1/chat/completions",
    },
    "perplexity": {
        "label": "Perplexity",
        "type": "openai",
        "env_key": "PERPLEXITY_API_KEY",
        "model_env": "PERPLEXITY_MODEL",
        "default_model": "sonar",
        "base_url": "https://api.perplexity.ai/chat/completions",
    },
    "fireworks": {
        "label": "Fireworks AI",
        "type": "openai",
        "env_key": "FIREWORKS_API_KEY",
        "model_env": "FIREWORKS_MODEL",
        "default_model": "accounts/fireworks/models/llama-v3p1-8b-instruct",
        "base_url": "https://api.fireworks.ai/inference/v1/chat/completions",
    },
    "cohere": {
        "label": "Cohere",
        "type": "cohere",
        "env_key": "COHERE_API_KEY",
        "model_env": "COHERE_MODEL",
        "default_model": "command-r-plus-08-2024",
    },
    "moonshot": {
        "label": "Moonshot (Kimi)",
        "type": "openai",
        "env_key": "MOONSHOT_API_KEY",
        "model_env": "MOONSHOT_MODEL",
        "default_model": "moonshot-v1-8k",
        "base_url": "https://api.moonshot.cn/v1/chat/completions",
    },
    "zhipu": {
        "label": "Zhipu GLM",
        "type": "openai",
        "env_key": "ZHIPU_API_KEY",
        "model_env": "ZHIPU_MODEL",
        "default_model": "glm-4-flash",
        "base_url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
    },
    "siliconflow": {
        "label": "SiliconFlow",
        "type": "openai",
        "env_key": "SILICONFLOW_API_KEY",
        "model_env": "SILICONFLOW_MODEL",
        "default_model": "deepseek-ai/DeepSeek-V2.5",
        "base_url": "https://api.siliconflow.cn/v1/chat/completions",
    },
    "ai21": {
        "label": "AI21 Labs",
        "type": "openai",
        "env_key": "AI21_API_KEY",
        "model_env": "AI21_MODEL",
        "default_model": "jamba-1.5-mini",
        "base_url": "https://api.ai21.com/studio/v1/chat/completions",
    },
    "azure": {
        "label": "Azure OpenAI",
        "type": "azure",
        "env_key": "AZURE_OPENAI_API_KEY",
        "endpoint_env": "AZURE_OPENAI_ENDPOINT",
        "model_env": "AZURE_OPENAI_DEPLOYMENT",
        "default_model": "gpt-4o-mini",
    },
    "ollama": {
        "label": "Ollama (Local)",
        "type": "ollama",
        "env_key": "OLLAMA_API_KEY",
        "base_url_env": "OLLAMA_BASE_URL",
        "model_env": "OLLAMA_MODEL",
        "default_model": "llama3.2",
        "enable_env": "OLLAMA_ENABLED",
    },
}

PROVIDER_PRIORITY = list(PROVIDER_CONFIG.keys())


def _is_placeholder(value: str) -> bool:
    lower = value.lower()
    return "your_" in lower or "_here" in lower or lower in ("", "none", "null", "changeme")


def _is_provider_configured(provider: str) -> bool:
    cfg = PROVIDER_CONFIG[provider]
    ptype = cfg["type"]

    if ptype == "ollama":
        if os.getenv(cfg.get("enable_env", ""), "").strip().lower() in ("1", "true", "yes"):
            return True
        base = os.getenv(cfg.get("base_url_env", "OLLAMA_BASE_URL"), "").strip()
        return bool(base)

    if ptype == "azure":
        key = os.getenv(cfg["env_key"], "").strip()
        endpoint = os.getenv(cfg.get("endpoint_env", "AZURE_OPENAI_ENDPOINT"), "").strip()
        return bool(key and endpoint and not _is_placeholder(key))

    key = os.getenv(cfg["env_key"], "").strip()
    return bool(key and not _is_placeholder(key))


def _get_api_key(provider: str) -> Optional[str]:
    if not _is_provider_configured(provider):
        return None
    cfg = PROVIDER_CONFIG[provider]
    if cfg["type"] == "ollama":
        return os.getenv(cfg.get("env_key", "OLLAMA_API_KEY"), "ollama").strip() or "ollama"
    return os.getenv(cfg["env_key"], "").strip()


def _get_model(provider: str) -> str:
    cfg = PROVIDER_CONFIG[provider]
    return os.getenv(cfg["model_env"], cfg["default_model"]).strip()


def _get_base_url(provider: str) -> str:
    cfg = PROVIDER_CONFIG[provider]
    if cfg["type"] == "ollama":
        base = os.getenv(cfg.get("base_url_env", "OLLAMA_BASE_URL"), "http://localhost:11434").strip()
        return f"{base.rstrip('/')}/v1/chat/completions"
    if cfg["type"] == "azure":
        endpoint = os.getenv(cfg.get("endpoint_env", "AZURE_OPENAI_ENDPOINT"), "").strip().rstrip("/")
        deployment = _get_model(provider)
        return f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-08-01-preview"
    return cfg["base_url"]


def get_available_providers() -> list[str]:
    return [p for p in PROVIDER_PRIORITY if _is_provider_configured(p)]


def get_provider_status() -> list[dict]:
    """All providers with configured flag and env var name."""
    status = []
    for pid in PROVIDER_PRIORITY:
        cfg = PROVIDER_CONFIG[pid]
        status.append({
            "id": pid,
            "label": cfg["label"],
            "configured": _is_provider_configured(pid),
            "env_key": cfg.get("env_key", ""),
        })
    return status


def resolve_provider(preferred: Optional[str] = None) -> Optional[str]:
    if preferred and preferred != "auto" and preferred in PROVIDER_CONFIG:
        return preferred if _is_provider_configured(preferred) else None

    env_provider = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    if env_provider and env_provider != "auto" and env_provider in PROVIDER_CONFIG:
        if _is_provider_configured(env_provider):
            return env_provider

    available = get_available_providers()
    return available[0] if available else None


def build_user_message(query: str, context: str, user_profile: dict) -> str:
    return f"Context: {context}\n\nUser Query: {query}\n\nUser Profile: {user_profile}"


def _chat_openai_compatible(
    url: str,
    api_key: str,
    model: str,
    user_message: str,
    extra_headers: Optional[dict] = None,
    use_model_in_body: bool = True,
) -> str:
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.3,
        "max_tokens": 800,
    }
    if use_model_in_body:
        payload["model"] = model

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)

    response = requests.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _chat_gemini(api_key: str, model: str, user_message: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_message}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 800},
    }
    response = requests.post(
        url, params={"key": api_key}, json=payload,
        headers={"Content-Type": "application/json"}, timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


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


def _chat_cohere(api_key: str, model: str, user_message: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.3,
        "max_output_tokens": 800,
    }
    response = requests.post(
        "https://api.cohere.com/v2/chat",
        json=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"][0]["text"]


def chat_completion(provider: str, user_message: str) -> str:
    api_key = _get_api_key(provider)
    if api_key is None:
        raise ValueError(f"Provider not configured: {provider}")

    cfg = PROVIDER_CONFIG[provider]
    model = _get_model(provider)
    ptype = cfg["type"]

    if ptype == "openai":
        return _chat_openai_compatible(
            _get_base_url(provider),
            api_key,
            model,
            user_message,
            extra_headers=cfg.get("extra_headers"),
        )
    if ptype == "azure":
        return _chat_openai_compatible(
            _get_base_url(provider), api_key, model, user_message, use_model_in_body=False,
        )
    if ptype == "ollama":
        return _chat_openai_compatible(_get_base_url(provider), api_key, model, user_message)
    if ptype == "gemini":
        return _chat_gemini(api_key, model, user_message)
    if ptype == "claude":
        return _chat_claude(api_key, model, user_message)
    if ptype == "cohere":
        return _chat_cohere(api_key, model, user_message)

    raise ValueError(f"Unknown provider type: {ptype}")


def _providers_to_try(preferred: Optional[str]) -> list[str]:
    if preferred and preferred != "auto":
        return [preferred] if preferred in PROVIDER_CONFIG else []
    return get_available_providers()


def llm_fallback(
    query: str,
    context: str = "",
    user_profile: Optional[dict] = None,
    provider: Optional[str] = None,
    disclaimer_fn: Optional[Callable[[], str]] = None,
) -> str:
    if disclaimer_fn is None:
        from utils.disclaimers import get_disclaimer
        disclaimer_fn = get_disclaimer

    user_profile = user_profile or {}
    user_message = build_user_message(query, context, user_profile)
    candidates = _providers_to_try(provider)

    if not candidates:
        lines = [f"• {PROVIDER_CONFIG[p]['label']} (`{PROVIDER_CONFIG[p].get('env_key', '')}`)" for p in PROVIDER_PRIORITY]
        return (
            "⚠️ No LLM API key configured. Add one or more keys to `.env` (see `.env.example`):\n"
            + "\n".join(lines)
            + f"\n\nHere's what I know locally: {context}"
            + disclaimer_fn()
        )

    errors = []
    for pid in candidates:
        if not _is_provider_configured(pid):
            continue
        try:
            content = chat_completion(pid, user_message)
            label = PROVIDER_CONFIG[pid]["label"]
            return f"_{label} response_\n\n{content}" + disclaimer_fn()
        except Exception as exc:
            errors.append(f"{PROVIDER_CONFIG[pid]['label']}: {exc}")

    tried = ", ".join(PROVIDER_CONFIG[p]["label"] for p in candidates if _is_provider_configured(p))
    return (
        f"Sorry, all configured providers failed ({tried}).\n"
        f"Here's what I know locally: {context}"
        + disclaimer_fn()
    )


def provider_label(provider_id: str) -> str:
    if provider_id == "auto":
        return "Auto (try all configured)"
    return PROVIDER_CONFIG.get(provider_id, {}).get("label", provider_id)