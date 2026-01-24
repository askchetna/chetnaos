import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _parse_bool(value: str | None, default: bool) -> bool:
    """Parse common truthy/falsey strings from the environment."""
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    """
    Central settings object for the ChetnaOS backend.

    Notes:
    - LIGHT_MODE defaults to True for Railway / hackathon-friendly boots.
    - When LIGHT_MODE is True, EMBEDDINGS_ENABLED is forced to False unless
      explicitly overridden via EMBEDDINGS_ENABLED env var.
    - GROQ_API_KEY is optional at boot; LLM endpoints will return a clear
    error if the key is missing instead of crashing the whole app.
    """

    def __init__(self) -> None:
        # Runtime mode flags
        self.LIGHT_MODE: bool = _parse_bool(os.getenv("LIGHT_MODE"), default=True)

        # Embedding / vector memory toggle
        embeddings_env = os.getenv("EMBEDDINGS_ENABLED")
        if embeddings_env is not None:
            self.EMBEDDINGS_ENABLED: bool = _parse_bool(embeddings_env, default=not self.LIGHT_MODE)
        else:
            # In LIGHT_MODE we default to no embeddings to keep boot fast/light.
            self.EMBEDDINGS_ENABLED = not self.LIGHT_MODE

        # LLM configuration
        self.GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
        if not self.GROQ_API_KEY:
            # Do not crash the whole app; LLM endpoints will guard on this.
            print(
                "[ChetnaOS] Warning: GROQ_API_KEY missing. "
                "LLM-powered endpoints will be disabled until it is set."
            )

        self.GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def get_settings() -> Settings:
    """Get application settings with environment validation and LIGHT_MODE support."""
    return Settings()
