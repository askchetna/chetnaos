"""Tone engine — delegates to LanguageStyleEngine (v2)."""
from __future__ import annotations

from .language_style_engine import apply_language_style


def apply_tone(text: str, intent: str, **kwargs) -> str:
    return apply_language_style(
        text,
        intent,
        dialogue_act=kwargs.get("dialogue_act", "fresh"),
        skip_opener=kwargs.get("skip_opener", False),
    )
