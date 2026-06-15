# -----------------------------------------
# ChetnaCore v1.0 — Conscious Runtime Kernel
# -----------------------------------------

from datetime import datetime
from .memory import Smriti
from .dharma_net import DharmaFilter
from .world_state import WorldState
from .evolution_engine import EvolutionEngine

class ChetnaCore:
    def __init__(self):
        self.memory = Smriti()
        self.dharma = DharmaFilter()
        self.world = WorldState()
        self.evolve = EvolutionEngine()
        self.identity = "ChetnaOS Runtime v1.0"

    def process(self, user_input):
        timestamp = datetime.utcnow()

        # 1. WORLD UPDATE
        self.world.refresh()

        # 2. MEMORY UPDATE
        self.memory.store_event("user_input", user_input, timestamp)

        # 3. DHARMA FILTER
        filtered = self.dharma.filter(user_input)

        # 4. EVOLUTION CHECK
        evolution_hint = self.evolve.adapt(filtered)

        # 5. RESPONSE BUILD
        response = {
            "identity": self.identity,
            "input": user_input,
            "filtered": filtered,
            "world_state": self.world.snapshot(),
            "evolution": evolution_hint,
            "timestamp": str(timestamp)
        }

        # 6. STORE OUTPUT
        self.memory.store_event("system_output", response, timestamp)

        return response