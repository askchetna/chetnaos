"""
Cognitive Cycle — The 27-stage locked cycle of ChetnaOS v2.0
Integrates: Simulation · MetaCognition · FounderContext ·
            Skills · WorkspaceState · ContradictionTracker · MemoryHierarchy
"""
from collections import deque

from src.chetnaos.organism.existence          import Existence
from src.chetnaos.organism.purpose            import Purpose
from src.chetnaos.organism.perception         import Perception
from src.chetnaos.organism.attention          import Attention
from src.chetnaos.organism.memory             import Memory
from src.chetnaos.organism.imagination        import Imagination
from src.chetnaos.organism.play               import Play
from src.chetnaos.organism.abstraction        import Abstraction
from src.chetnaos.organism.world_model        import WorldModel
from src.chetnaos.organism.reasoning          import Reasoning
from src.chetnaos.organism.planning           import Planning
from src.chetnaos.organism.decision           import Decision
from src.chetnaos.organism.embodiment         import Embodiment
from src.chetnaos.organism.habit              import Habit
from src.chetnaos.organism.experience         import Experience
from src.chetnaos.organism.reality            import RealityChecker
from src.chetnaos.organism.reflection         import Reflection
from src.chetnaos.organism.learning           import Learning
from src.chetnaos.organism.beliefs            import Beliefs
from src.chetnaos.organism.identity           import Identity
from src.chetnaos.organism.development        import Development
from src.chetnaos.organism.homeostasis        import Homeostasis
from src.chetnaos.organism.sleep              import Sleep
from src.chetnaos.organism.relationship       import Relationship
from src.chetnaos.organism.artifacts          import Artifacts
from src.chetnaos.organism.civilization_memory import CivilizationMemory
# v2 modules
from src.chetnaos.organism.founder_context    import FounderContext
from src.chetnaos.organism.simulation         import SimulationEngine
from src.chetnaos.organism.meta_cognition     import MetaCognition
# New dashboard modules
from src.chetnaos.organism.skills             import Skills
from src.chetnaos.organism.workspace_state    import WorkspaceState
from src.chetnaos.organism.contradiction_tracker import ContradictionTracker
from src.chetnaos.organism.memory_hierarchy   import MemoryHierarchy
from src.chetnaos.organism.self_trainer       import SelfTrainer

from .state_machine import StateMachine, CycleStage
from .sleep_manager import SleepManager
from .llm_router    import LLMRouter


class CognitiveCycle:
    def __init__(self):
        # Orchestrator
        self.llm     = LLMRouter()
        self.sm      = StateMachine()
        self.sleeper = SleepManager()

        # Core organism modules
        self.existence   = Existence()
        self.purpose     = Purpose()
        self.perception  = Perception()
        self.attention   = Attention()
        self.memory      = Memory()
        self.imagination = Imagination()
        self.play_mod    = Play()
        self.abstraction = Abstraction()
        self.world       = WorldModel()
        self.reasoning   = Reasoning()
        self.planning    = Planning()
        self.decision    = Decision()
        self.embodiment  = Embodiment()
        self.habit       = Habit()
        self.experience  = Experience()
        self.reality     = RealityChecker()
        self.reflection  = Reflection()
        self.learning    = Learning()
        self.beliefs     = Beliefs()
        self.identity    = Identity()
        self.development = Development()
        self.homeostasis = Homeostasis()
        self.sleep_mod   = Sleep()
        self.relationship = Relationship()
        self.artifacts   = Artifacts()
        self.civ_memory  = CivilizationMemory()

        # v2 modules
        self.founder_ctx = FounderContext()
        self.simulation  = SimulationEngine()
        self.meta_cog    = MetaCognition()

        # Dashboard modules
        self.skills         = Skills()
        self.workspace      = WorkspaceState()
        self.contradictions = ContradictionTracker()
        self.mem_hierarchy  = MemoryHierarchy()
        self.self_trainer   = SelfTrainer()

        # In-memory session state
        self._recent_reality_checks: deque = deque(maxlen=8)
        self._last_sim          = {}
        self._last_meta         = {}
        self._last_thought_birth = {}
        self._last_sleep_data   = {}
        self._training_goals    = self.self_trainer.get()

    # ──────────────────────────────────────────────────────────────────────
    def run(self, user_input: str, mode: str = "chat") -> dict:
        trace: list[dict] = []

        def step(stage: CycleStage, result: dict):
            self.sm.advance(stage)
            trace.append({"stage": stage.value,
                          **{k: v for k, v in result.items() if k != "stage"}})
            return result

        # ── EXIST ──────────────────────────────────────────────────────
        exist_r = step(CycleStage.EXIST, self.existence.pulse())
        cycle_n = exist_r["cycle"]

        # ── PURPOSE ────────────────────────────────────────────────────
        purpose_r = step(CycleStage.PURPOSE, self.purpose.get())

        # ── OBSERVE ────────────────────────────────────────────────────
        percept = self.perception.perceive(user_input)
        step(CycleStage.OBSERVE, percept)

        # ── ATTEND ─────────────────────────────────────────────────────
        att = self.attention.attend(percept)
        step(CycleStage.ATTEND, att)
        # Working memory: push current input
        self.mem_hierarchy.push_working({
            "input": user_input[:100], "intent": percept.get("intent"),
        })

        # ── RECALL ─────────────────────────────────────────────────────
        recalled   = self.memory.recall(user_input, k=4)
        founder_ctx_str = self.founder_ctx.get_system_context()
        step(CycleStage.RECALL, {
            "recalled_count": len(recalled),
            "founder_context_loaded": True,
        })

        # ── PREDICT ────────────────────────────────────────────────────
        abstr = self.abstraction.abstract(percept, att)
        step(CycleStage.PREDICT, {**abstr})
        self.mem_hierarchy.add_semantic(abstr.get("domain", "general"))

        # ── IMAGINE ────────────────────────────────────────────────────
        use_llm = abstr["complexity"] == "complex"
        imag = self.imagination.imagine(att, self.llm if use_llm else None)
        step(CycleStage.IMAGINE, imag)

        # ── PLAY ───────────────────────────────────────────────────────
        play_r = self.play_mod.explore(att, imag)
        step(CycleStage.PLAY, play_r)

        # ── PLAN + SIMULATION ──────────────────────────────────────────
        plan_r = self.planning.plan(play_r, abstr, self.llm if use_llm else None)
        sim_r  = self.simulation.simulate(plan_r["plan"], abstr,
                                          self.llm if use_llm else None)
        selected_plan = sim_r["selected"]
        step(CycleStage.PLAN, {**plan_r, "simulation": sim_r})
        self._last_sim = sim_r

        # Update workspace: plan is now active
        self.workspace.update(user_input, selected_plan, abstr["domain"], "fair", att)

        # ── HABIT ──────────────────────────────────────────────────────
        habit_r = self.habit.check(percept["intent"], abstr["domain"])
        step(CycleStage.HABIT, habit_r)

        # ── ACT (primary LLM call) ─────────────────────────────────────
        reason_r     = self.reasoning.reason(
            user_input, recalled, selected_plan, self.llm,
            founder_context=founder_ctx_str,
        )
        raw_response = reason_r["response"]
        step(CycleStage.ACT, reason_r)

        # Thought Birth record
        self._last_thought_birth = {
            "sense":       user_input[:100],
            "memory":      [m.get("text", "")[:80] for m in recalled[:2]],
            "imagination": imag.get("possibilities", [])[:3],
            "trigger":     percept.get("intent", "statement"),
            "new_thought": raw_response[:200],
        }

        # ── WORLD UPDATE ───────────────────────────────────────────────
        world_r = self.world.update(att, abstr)
        step(CycleStage.WORLD_UPDATE, world_r)

        # ── EXPERIENCE ─────────────────────────────────────────────────
        exp_r = self.experience.record({
            "input": user_input, "output": raw_response,
            "domain": abstr["domain"], "cycle_count": cycle_n, "confidence": 0.6,
        })
        step(CycleStage.EXPERIENCE, exp_r)

        # ── REALITY CHECK ──────────────────────────────────────────────
        reality_r = self.reality.check(raw_response, {"beliefs": self.beliefs.get_all()})
        step(CycleStage.REALITY_CHECK, reality_r)
        # Log for dashboard
        self._recent_reality_checks.appendleft({
            "statement":  user_input[:80],
            "confidence": reality_r["confidence"],
            "level":      reality_r["confidence_level"],
            "truth":      reality_r["truth_estimate"],
            "passed":     reality_r["passed"],
            "cycle":      cycle_n,
        })

        # ── EVALUATE ───────────────────────────────────────────────────
        dec_r = self.decision.decide(reason_r, reality_r)
        step(CycleStage.EVALUATE, dec_r)

        # ── FAILURE RECOVERY ───────────────────────────────────────────
        final_output = dec_r["final"]
        step(CycleStage.FAILURE_RECOVERY, {"recovered": False, "output": final_output})

        # ── REFLECT ────────────────────────────────────────────────────
        reflect_r = self.reflection.reflect(dec_r, reality_r, {
            "intent": percept["intent"], "risk_level": "low",
        })
        step(CycleStage.REFLECT, reflect_r)

        # Skills: practice based on domain and quality, then refresh training goals
        self.skills.practice(abstr["domain"], reflect_r["quality"])
        self._training_goals = self.self_trainer.generate_goals(self.skills.get_all())

        # ── SELF QUESTION + META-COGNITION ─────────────────────────────
        meta_r = self.meta_cog.evaluate(percept, dec_r, reflect_r, reality_r)
        self._last_meta = meta_r
        step(CycleStage.SELF_QUESTION, {
            "question": f"Did I serve '{percept['intent']}' truthfully?",
            "answer":   "yes" if reflect_r["quality"] in ("good","fair") else "needs_improvement",
            "meta":     meta_r,
        })

        # ── UPDATE BELIEFS ─────────────────────────────────────────────
        learn_r   = self.learning.learn(reflect_r, exp_r)
        beliefs_r = self.beliefs.update(reflect_r, learn_r)
        step(CycleStage.UPDATE_BELIEFS, beliefs_r)
        # Contradiction scan — beliefs, memories, and founder mission
        contradictions = self.contradictions.scan(self.beliefs.get_all())
        self.contradictions.scan_memory(
            self.beliefs.get_all(), self.memory.recall(user_input, k=5)
        )
        self.contradictions.scan_founder(
            self.beliefs.get_all(), self.founder_ctx.get().get("primary_mission", "")
        )
        self.workspace.set_contradictions(self.contradictions.count())

        # ── UPDATE IDENTITY ────────────────────────────────────────────
        identity_r = self.identity.update(reflect_r, beliefs_r)
        self.identity.tick()
        step(CycleStage.UPDATE_IDENTITY, identity_r)

        # ── REFINE PURPOSE ─────────────────────────────────────────────
        if reflect_r["quality"] == "good":
            self.purpose.refine(
                f"Handled {abstr['domain']} {percept['intent']} well "
                f"(dharma={reflect_r['dharma_score']})."
            )
        step(CycleStage.REFINE_PURPOSE, self.purpose.get())

        # ── SLEEP / FORGET / CONSOLIDATE / WAKE ────────────────────────
        slept = False
        sleep_data = {}
        if self.sleeper.should_sleep(cycle_n):
            sleep_r = self.sleep_mod.consolidate(self.beliefs, self.memory, cycle_n)
            step(CycleStage.SLEEP,       sleep_r)
            step(CycleStage.FORGET,      {"forgotten": sleep_r.get("forgotten", 0)})
            step(CycleStage.CONSOLIDATE, {"consolidated": sleep_r.get("consolidated", 0)})
            step(CycleStage.WAKE,        self.sleep_mod.wake())
            self.sleeper.mark_slept(cycle_n)
            self.mem_hierarchy.record_forgetting(sleep_r.get("forgotten", 0))
            slept = True
            sleep_data = sleep_r
            self._last_sleep_data = sleep_r
        else:
            next_in = self.sleeper.cycles_until_sleep(cycle_n)
            step(CycleStage.SLEEP,       {"slept": False, "next_in": next_in})
            step(CycleStage.FORGET,      {"forgotten": 0})
            step(CycleStage.CONSOLIDATE, {"consolidated": 0})
            step(CycleStage.WAKE,        {"refreshed": True})

        # ── Side effects ───────────────────────────────────────────────
        dev_r  = self.development.record(reflect_r, reality_r["confidence"])
        home_r = self.homeostasis.check(dev_r, reflect_r)
        self.habit.record(percept["intent"], abstr["domain"])
        self.relationship.update("user")
        self.artifacts.store(final_output, abstr["domain"], percept["intent"])
        self.civ_memory.contribute(reflect_r["cycle_score"], final_output, abstr["domain"])
        self.memory.store("interaction", f"Q: {user_input[:200]}\nA: {final_output[:300]}")

        # Workspace artifact
        if len(final_output) > 150:
            self.workspace.add_artifact(
                f"{abstr['domain']}_response_{cycle_n}.txt", "response"
            )

        # Memory hierarchy: add unsolved question if quality was poor
        if reflect_r["quality"] == "poor":
            self.workspace.add_question(f"Why did cycle {cycle_n} score poorly?")
            self.mem_hierarchy.add_dream(user_input[:80])

        self.sm.complete_cycle()

        return {
            "reply":            final_output,
            "cycle":            cycle_n,
            "stage_trace":      [t["stage"] for t in trace],
            "confidence":       reality_r["confidence"],
            "confidence_level": reality_r["confidence_level"],
            "dharma_score":     reflect_r["dharma_score"],
            "cycle_score":      reflect_r["cycle_score"],
            "quality":          reflect_r["quality"],
            "domain":           abstr["domain"],
            "intent":           percept["intent"],
            "beliefs_count":    beliefs_r["count"],
            "slept":            slept,
            "health":           home_r["health"],
            "identity":         identity_r["identity"]["name"],
            "purpose":          purpose_r.get("statement", ""),
            "reality": {
                "passed":     reality_r["passed"],
                "confidence": reality_r["confidence"],
                "level":      reality_r["confidence_level"],
                "truth":      reality_r["truth_estimate"],
            },
            "simulation":     sim_r,
            "meta_cognition": {
                "why":          meta_r["why"],
                "was_correct":  meta_r["was_correct"],
                "correctness":  meta_r["correctness"],
                "can_improve":  meta_r["can_improve"],
                "self_verdict": meta_r["self_verdict"],
            },
            "trace": trace,
        }

    # ──────────────────────────────────────────────────────────────────────
    def dashboard_snapshot(self) -> dict:
        """Full cognitive state for the dashboard page."""
        id_data  = self.identity.get()
        dev_data = self.development._data
        total    = max(dev_data.get("total_cycles", 1), 1)
        good     = dev_data.get("good_cycles", 0)
        poor     = dev_data.get("poor_cycles", 0)
        stability = round(min(99, max(10, (good / total) * 100 + 50)), 1) if total > 1 else 80.0

        return {
            "identity": {
                **id_data,
                "stability":           stability,
                "drift":               round(100 - stability, 1),
                "core_values_preserved": True,
                "roles": ["Founder Partner", "Research Organism",
                          "AI Consultant", "Learning System"],
            },
            "skills": {
                "ranked":    self.skills.get_ranked(),
                "transfers": self.skills.get_transfers(),
            },
            "workspace":       self.workspace.get(),
            "memory":          self.mem_hierarchy.snapshot(),
            "beliefs": {
                "all":   self.beliefs.get_all(),
                "count": len(self.beliefs.get_all()),
            },
            "contradictions":  self.contradictions.get(),
            "development": {
                **dev_data,
                "total_cycles": total,
            },
            "sleep": {
                "cycles_until_next": self.sleeper.cycles_until_sleep(
                    self.existence.cycle_count
                ),
                "sleep_every": self.sleeper._sleep_every,
            },
            "reality_checks":  list(self._recent_reality_checks),
            "simulation":      self._last_sim,
            "meta_cognition":  self._last_meta,
            "thought_birth":   self._last_thought_birth,
            "health":          self.homeostasis.check(
                {"stats": dev_data}, {"quality": "fair"}
            ),
            "founder_context": self.founder_ctx.get(),
            "world":           self.world.snapshot(),
            "training_goals":  self._training_goals,
            "last_sleep":      self._last_sleep_data,
            "last_sleep_log":  self.sleep_mod.get_last_sleep(),
        }
