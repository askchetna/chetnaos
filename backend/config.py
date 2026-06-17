import os
from dotenv import load_dotenv

from memory.embedding_config import resolve_embedding_settings

# Load environment variables from .env file
load_dotenv()


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
        # Runtime mode flags (shared resolver with memory/db.py)
        self.LIGHT_MODE, self.EMBEDDINGS_ENABLED = resolve_embedding_settings()

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
