# Copyright (c) 2026 AI Software Innovation Infotech And Hardware Enterprises. All Rights Reserved.
"""
LLM Client v5.0 — OpenRouter (free models) + OpenAI + Anthropic + xAI
OpenRouter: https://openrouter.ai — key format sk-or-v1-...
"""

import os
from typing import Optional, List, Dict

def _get_secret(key: str) -> Optional[str]:
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            val = st.secrets[key]
            if val:
                return str(val).strip()
    except Exception:
        pass
    return os.environ.get(key)


def has_any_llm_key() -> bool:
    return bool(
        _get_secret("OPENROUTER_API_KEY")
        or _get_secret("OPENAI_API_KEY")
        or _get_secret("ANTHROPIC_API_KEY")
        or _get_secret("XAI_API_KEY")
        or _get_secret("GROK_API_KEY")
    )


def has_openrouter_key() -> bool:
    return bool(_get_secret("OPENROUTER_API_KEY"))


# Free-friendly models on OpenRouter (may change; user can override)
OPENROUTER_FREE_MODELS = [
    "google/gemma-2-9b-it:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "openrouter/auto",
    "google/gemini-2.0-flash-exp:free",
]


def chat_with_llm(
    messages: List[Dict[str, str]],
    provider: str = "auto",
    model: Optional[str] = None,
) -> Optional[str]:
    provider = (provider or "auto").lower()

    if provider == "auto":
        if _get_secret("OPENROUTER_API_KEY"):
            provider = "openrouter"
        elif _get_secret("OPENAI_API_KEY"):
            provider = "openai"
        elif _get_secret("ANTHROPIC_API_KEY"):
            provider = "anthropic"
        elif _get_secret("XAI_API_KEY") or _get_secret("GROK_API_KEY"):
            provider = "xai"
        else:
            return None

    try:
        if provider in ("openrouter", "or"):
            return _openrouter_chat(messages, model)
        if provider == "openai":
            return _openai_chat(messages, model or "gpt-4o-mini")
        if provider == "anthropic":
            return _anthropic_chat(messages, model or "claude-3-5-sonnet-20241022")
        if provider in ("xai", "grok"):
            return _xai_chat(messages, model or "grok-beta")
        return None
    except Exception as e:
        return f"[LLM Error: {str(e)[:280]}]"


def _openrouter_chat(messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
    from openai import OpenAI
    key = _get_secret("OPENROUTER_API_KEY")
    if not key:
        raise ValueError("OPENROUTER_API_KEY not found in Secrets")

    client = OpenAI(
        api_key=key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://streamlit.io",
            "X-Title": "AISIH Multi-Agent Gateway v5",
        },
    )

    # Prefer free model if not specified
    use_model = model or OPENROUTER_FREE_MODELS[0]
    last_err = None

    # Try free models in order if default fails
    models_to_try = [use_model] + [m for m in OPENROUTER_FREE_MODELS if m != use_model]

    for m in models_to_try[:4]:
        try:
            resp = client.chat.completions.create(
                model=m,
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
            )
            content = resp.choices[0].message.content
            return content or ""
        except Exception as e:
            last_err = e
            continue
    raise last_err or RuntimeError("OpenRouter all models failed")


def _openai_chat(messages, model: str) -> str:
    from openai import OpenAI
    key = _get_secret("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY not found")
    client = OpenAI(api_key=key)
    resp = client.chat.completions.create(
        model=model, messages=messages, temperature=0.7, max_tokens=2048
    )
    return resp.choices[0].message.content or ""


def _anthropic_chat(messages, model: str) -> str:
    from anthropic import Anthropic
    key = _get_secret("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not found")
    client = Anthropic(api_key=key)
    system = ""
    chat_msgs = []
    for m in messages:
        if m["role"] == "system":
            system = m["content"]
        else:
            chat_msgs.append({"role": m["role"], "content": m["content"]})
    kwargs = {"model": model, "max_tokens": 2048, "messages": chat_msgs}
    if system:
        kwargs["system"] = system
    resp = client.messages.create(**kwargs)
    return resp.content[0].text if resp.content else ""


def _xai_chat(messages, model: str) -> str:
    from openai import OpenAI
    key = _get_secret("XAI_API_KEY") or _get_secret("GROK_API_KEY")
    if not key:
        raise ValueError("XAI_API_KEY not found")
    client = OpenAI(api_key=key, base_url="https://api.x.ai/v1")
    resp = client.chat.completions.create(
        model=model, messages=messages, temperature=0.7, max_tokens=2048
    )
    return resp.choices[0].message.content or ""
