"""ChetnaOS Runtime — application entry (canonical v3 location)."""
from src.chetnaos.cycle.cognitive_cycle import CognitiveCycle

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

    def process(self, user_input: str, mode: str = "chat", **kwargs) -> dict:
        return self._cycle.run(user_input, mode=mode, **kwargs)

    def session_snapshot(self) -> dict:
        """Workspace state for refresh-safe UI."""
        c = self._cycle
        return {
            "active_goal": c.goal_manager.active_goal(),
            "current_thought": c._last_thought_birth,
            "working_memory": c.working_memory.recall(),
            "memory_influence": c._last_memory_influence,
            "belief_influence": c._last_belief_influence,
            "belief_changes": c._last_belief_changes,
            "contradiction_resolutions": c.contradictions.resolution_history()[:5],
        }

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

    @property
    def active_goal(self) -> dict | None:
        return self._cycle.goal_manager.active_goal()
