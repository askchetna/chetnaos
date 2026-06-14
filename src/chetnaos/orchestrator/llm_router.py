"""
LLM Router — Routes all LLM calls through Groq.
Single point of contact for language model inference.
"""
import os
from groq import Groq


class LLMRouter:
    DEFAULT_MODEL = "llama-3.1-8b-instant"

    def __init__(self):
        self._api_key = os.getenv("GROQ_API_KEY")
        self._model   = os.getenv("GROQ_MODEL", self.DEFAULT_MODEL)
        self._client  = None

    def _get_client(self) -> Groq:
        if not self._api_key:
            self._api_key = os.getenv("GROQ_API_KEY")
        if not self._api_key:
            raise RuntimeError("GROQ_API_KEY not set. LLM features unavailable.")
        if self._client is None:
            self._client = Groq(api_key=self._api_key)
        return self._client

    def complete(self, prompt: str, system: str = "", max_tokens: int = 256,
                 temperature: float = 0.3) -> str:
        """Single-turn completion."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages, max_tokens=max_tokens, temperature=temperature)

    def chat(self, messages: list, max_tokens: int = 1024,
             temperature: float = 0.4) -> str:
        """Multi-turn chat completion."""
        client = self._get_client()
        resp = client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content

    @property
    def model(self) -> str:
        return self._model

    @property
    def available(self) -> bool:
        return bool(os.getenv("GROQ_API_KEY"))
