# Copyright (c) 2026 AI Software Innovation Infotech And Hardware Enterprises. All Rights Reserved.
"""Image generation via OpenAI DALL·E (and ready for other APIs)."""

import os
import base64
from typing import Optional, Tuple

def _get_secret(key: str) -> Optional[str]:
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key)


def has_openai_image_key() -> bool:
    return bool(_get_secret("OPENAI_API_KEY"))


def generate_image_openai(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "standard",
    model: str = "dall-e-3",
) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Returns (image_bytes, error_message).
    On success error_message is None.
    """
    key = _get_secret("OPENAI_API_KEY")
    if not key:
        return None, "OPENAI_API_KEY not found. Add it in Streamlit Secrets."

    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)

        # DALL·E 3 sizes: 1024x1024, 1792x1024, 1024x1792
        if size not in ("1024x1024", "1792x1024", "1024x1792"):
            size = "1024x1024"

        resp = client.images.generate(
            model=model,
            prompt=prompt[:4000],
            size=size,
            quality=quality if model == "dall-e-3" else "standard",
            n=1,
            response_format="b64_json",
        )
        b64 = resp.data[0].b64_json
        if not b64:
            return None, "No image data returned from API."
        return base64.b64decode(b64), None
    except Exception as e:
        return None, str(e)[:300]


def build_image_prompt(idea: str, style: str) -> str:
    """Build a strong prompt for DALL·E / Midjourney style."""
    return (
        f"A high-quality {style} image of {idea}, "
        "detailed, well-lit, clean composition, professional quality, no text, no watermark"
    )
