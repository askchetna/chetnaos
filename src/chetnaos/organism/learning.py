"""
Learning — Extracts lessons from the reflection and stores them.
"""
import json, os

LESSONS_FILE = os.path.join(os.path.dirname(__file__), "../../..", "memory", "lessons.jsonl")


class Learning:
    def learn(self, reflection: dict, experience: dict) -> dict:
        quality = reflection.get("quality", "fair")
        corrections = reflection.get("corrections", [])
        lessons = []

        if corrections:
            for c in corrections[:2]:
                lessons.append({"lesson": c, "quality": quality})

        if quality == "poor":
            lessons.append({
                "lesson": "This interaction scored poorly — review dharma alignment.",
                "quality": quality,
            })
        elif quality == "good" and not corrections:
            lessons.append({
                "lesson": "High-quality interaction — pattern worth repeating.",
                "quality": quality,
            })

        for lesson in lessons:
            self._store(lesson)

        return {
            "stage": "LEARN",
            "lessons_extracted": len(lessons),
            "lessons": lessons,
        }

    def _store(self, lesson: dict):
        try:
            p = os.path.abspath(LESSONS_FILE)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "a") as f:
                f.write(json.dumps(lesson) + "\n")
        except Exception:
            pass
