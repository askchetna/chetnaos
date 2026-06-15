# ---------------------------
# Dharma Filter v1.0
# ---------------------------

class DharmaFilter:
    SAFE = ["help", "support", "create", "learn", "guide", "improve"]
    UNSAFE = ["harm", "violence", "kill", "attack", "illegal"]

    def filter(self, text):
        t = text.lower()
        for bad in self.UNSAFE:
            if bad in t:
                return f"[BLOCKED — non-dharmic content detected]"
        return text