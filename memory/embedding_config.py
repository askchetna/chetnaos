"""Shared LIGHT_MODE / EMBEDDINGS_ENABLED resolution for memory + backend."""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def _parse_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def resolve_embedding_settings() -> tuple[bool, bool]:
    """
    Resolve runtime embedding flags from environment.

    Priority:
    - If EMBEDDINGS_ENABLED env var is set (including empty string is NOT set —
      only absent vs present matters), use its parsed boolean value.
    - Otherwise EMBEDDINGS_ENABLED defaults to ``not LIGHT_MODE``.
  """
    light_mode = _parse_bool(os.getenv("LIGHT_MODE"), default=True)
    embeddings_env = os.getenv("EMBEDDINGS_ENABLED")
    if embeddings_env is not None:
        embeddings_enabled = _parse_bool(embeddings_env, default=not light_mode)
    else:
        embeddings_enabled = not light_mode
    return light_mode, embeddings_enabled


_LIGHT_MODE, _EMBEDDINGS_ENABLED = resolve_embedding_settings()


def get_light_mode() -> bool:
    return _LIGHT_MODE


def get_embeddings_enabled() -> bool:
    return _EMBEDDINGS_ENABLED


def refresh_embedding_config() -> tuple[bool, bool]:
    """Re-read environment (e.g. after load_dotenv in another module)."""
    global _LIGHT_MODE, _EMBEDDINGS_ENABLED
    _LIGHT_MODE, _EMBEDDINGS_ENABLED = resolve_embedding_settings()
    return _LIGHT_MODE, _EMBEDDINGS_ENABLED
