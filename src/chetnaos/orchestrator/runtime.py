"""
ChetnaOS Runtime — Application-level entry point.
One singleton per process.
"""
from .cognitive_cycle import CognitiveCycle

_instance: CognitiveCycle | None = None


def get_runtime() -> CognitiveCycle:
    global _instance
    if _instance is None:
        _instance = CognitiveCycle()
    return _instance


class ChetnaRuntime:
    """Facade used by FastAPI routes."""

    def __init__(self):
        self._cycle = get_runtime()

    def process(self, user_input: str, mode: str = "chat") -> dict:
        return self._cycle.run(user_input, mode=mode)

    @property
    def identity(self) -> dict:
        return self._cycle.identity.get()

    @property
    def beliefs(self) -> list:
        return self._cycle.beliefs.get_all()

    @property
    def world(self) -> dict:
        return self._cycle.world.snapshot()

    @property
    def development(self) -> dict:
        return self._cycle.development._data

    @property
    def llm_available(self) -> bool:
        return self._cycle.llm.available

    @property
    def cognitive_organs(self) -> dict:
        return self._cycle._runtime_inspection_snapshot()
