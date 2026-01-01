# -----------------------------------------
# Evolution Engine v1.0 (Self-Healing Loop)
# -----------------------------------------

class EvolutionEngine:
    def __init__(self):
        self.health = 100

    def adapt(self, filtered_input):
        if "blocked" in filtered_input.lower():
            self.health -= 1
            return "Self-correction activated"
        else:
            if self.health < 100:
                self.health += 1
            return "Stable"