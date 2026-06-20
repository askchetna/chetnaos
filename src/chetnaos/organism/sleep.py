"""
Sleep — Consolidation phase with Dream/Replay mechanism.
Gap 5: Offline memory consolidation — replay experiences, extract patterns.

During sleep:
  1. Forget weak beliefs (confidence < 0.3)
  2. Dream Replay: re-read recent experiences, extract patterns
  3. Strengthen high-confidence beliefs
  4. Generate 1-2 "dream insights" from experience patterns
"""
import json, os, re
from datetime import datetime

SLEEP_LOG  = os.path.join(os.path.dirname(__file__), "../../..", "memory", "sleep_log.jsonl")
EXP_FILE   = os.path.join(os.path.dirname(__file__), "../../..", "memory", "experiences.jsonl")


class Sleep:
    SLEEP_EVERY = 20

    def consolidate(
        self,
        beliefs_module,
        memory_module,
        cycle_count: int,
        *,
        identity_module=None,
        relationship_module=None,
        development_module=None,
        reflection_organ=None,
    ) -> dict:
        """Full sleep consolidation with dream replay."""
        log = {
            "timestamp": datetime.utcnow().isoformat(),
            "cycle":     cycle_count,
            "action":    "sleep_consolidation",
        }

        # ── Phase 1: Forget weak beliefs ────────────────────────────────
        all_beliefs = beliefs_module.get_all()
        before      = len(all_beliefs)
        beliefs_module._beliefs = [b for b in all_beliefs if b.get("confidence", 1.0) >= 0.3]
        forgotten   = before - len(beliefs_module._beliefs)
        beliefs_module._save()
        log["forgotten_beliefs"] = forgotten

        # ── Phase 2: Strengthen high-confidence beliefs ──────────────────
        strengthened = 0
        for b in beliefs_module._beliefs:
            if b.get("confidence", 0) >= 0.8:
                b["confidence"] = min(0.99, b["confidence"] + 0.01)
                strengthened += 1
        if strengthened:
            beliefs_module._save()
        log["strengthened"] = strengthened

        # ── Phase 3: Dream Replay ────────────────────────────────────────
        recent_exps = self._load_recent_experiences(n=10)
        dream_insights = self._dream_replay(recent_exps)
        log["dream_replayed"]  = len(recent_exps)
        log["dream_insights"]  = dream_insights
        log["dreams"]          = dream_insights

        # ── Phase 4: Store dream insights as weak new beliefs ────────────
        new_beliefs = 0
        for insight in dream_insights:
            insight_text = insight.get("insight", "")
            if insight_text and len(insight_text) > 10:
                existing_texts = [b.get("text", "").lower() for b in beliefs_module._beliefs]
                if insight_text.lower() not in existing_texts:
                    beliefs_module._beliefs.append({
                        "text":        insight_text,
                        "confidence":  0.40,
                        "source":      "dream_consolidation",
                        "created_at":  datetime.utcnow().isoformat(),
                    })
                    new_beliefs += 1
        if new_beliefs:
            beliefs_module._save()
        log["new_beliefs_from_dreams"] = new_beliefs

        # ── Phase 5: Themes, relationships, identity, lessons ────────────
        domain_counts: dict[str, int] = {}
        for exp in recent_exps:
            d = exp.get("domain", "general")
            domain_counts[d] = domain_counts.get(d, 0) + 1
        themes = list(domain_counts.keys()) if domain_counts else []
        if development_module and themes:
            for theme in themes[:3]:
                development_module.add_theme(theme)
        if development_module and dream_insights:
            for ins in dream_insights[:2]:
                development_module.add_lesson(ins.get("insight", "")[:200])
        if relationship_module:
            relationship_module.strengthen_after_sleep()
        if identity_module:
            identity_module.after_sleep(dream_insights)
        if reflection_organ and dream_insights:
            for ins in dream_insights[:2]:
                reflection_organ.record(
                    ins.get("insight", ""),
                    source="sleep_consolidation",
                )

        self._log(log)
        return {
            "stage":           "SLEEP",
            "slept":           True,
            "forgotten":       forgotten,
            "consolidated":    len(beliefs_module._beliefs),
            "strengthened":    strengthened,
            "dream_replayed":  len(recent_exps),
            "dream_insights":  dream_insights,
            "new_beliefs":     new_beliefs,
        }

    def _load_recent_experiences(self, n: int = 10) -> list:
        try:
            p = os.path.abspath(EXP_FILE)
            if not os.path.exists(p):
                return []
            with open(p) as f:
                lines = [l.strip() for l in f if l.strip()]
            recent = lines[-n:]
            return [json.loads(l) for l in recent]
        except Exception:
            return []

    def _dream_replay(self, experiences: list) -> list:
        """Extract patterns from recent experiences to form insights."""
        if not experiences:
            return []

        domain_counts: dict[str, int]     = {}
        quality_counts: dict[str, int]    = {}
        common_phrases: list[str]         = []

        for exp in experiences:
            d = exp.get("domain", "general")
            domain_counts[d] = domain_counts.get(d, 0) + 1
            q = exp.get("quality", "fair")
            quality_counts[q] = quality_counts.get(q, 0) + 1
            out = exp.get("output", "")
            # Extract short imperative phrases as potential insights
            sentences = re.split(r'[.।!]', out)
            for s in sentences:
                s = s.strip()
                if 20 < len(s) < 90 and any(
                    kw in s.lower() for kw in
                    ["important", "key", "must", "always", "never", "critical", "essential", "best"]
                ):
                    common_phrases.append(s)

        insights = []

        # Insight from dominant domain
        if domain_counts:
            top_domain = max(domain_counts, key=domain_counts.get)
            if domain_counts[top_domain] >= 2:
                insights.append({
                    "insight":  f"Repeated exposure to '{top_domain}' domain — likely a core interest area.",
                    "source":   "pattern_replay",
                    "strength": 0.45,
                })

        # Insight from quality pattern
        good = quality_counts.get("good", 0)
        poor = quality_counts.get("poor", 0)
        if good > 0 and poor == 0:
            insights.append({
                "insight":  "Consistent high-quality responses in recent cycles — performance is stable.",
                "source":   "quality_replay",
                "strength": 0.50,
            })
        elif poor > good:
            insights.append({
                "insight":  "Several recent poor cycles — identify weakness and adjust approach.",
                "source":   "quality_replay",
                "strength": 0.55,
            })

        # Insight from extracted phrases
        if common_phrases:
            insights.append({
                "insight":  common_phrases[0][:80],
                "source":   "experience_replay",
                "strength": 0.42,
            })

        return insights[:3]

    def _log(self, entry: dict):
        try:
            p = os.path.abspath(SLEEP_LOG)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "a") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def get_last_sleep(self) -> dict:
        try:
            p = os.path.abspath(SLEEP_LOG)
            if not os.path.exists(p):
                return {}
            with open(p) as f:
                lines = [l.strip() for l in f if l.strip()]
            if lines:
                return json.loads(lines[-1])
        except Exception:
            pass
        return {}

    def wake(self) -> dict:
        return {"stage": "WAKE", "refreshed": True, "timestamp": datetime.utcnow().isoformat()}
