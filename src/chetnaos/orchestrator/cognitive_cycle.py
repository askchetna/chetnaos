"""
Cognitive Cycle — The 27-stage locked cycle of ChetnaOS.

EXIST → PURPOSE → OBSERVE → ATTEND → RECALL → PREDICT → IMAGINE →
PLAY → PLAN → DECIDE → ACT → HABIT → WORLD_UPDATE → EXPERIENCE →
REALITY_CHECK → EVALUATE → FAILURE_RECOVERY → REFLECT → SELF_QUESTION →
UPDATE_BELIEFS → UPDATE_IDENTITY → REFINE_PURPOSE →
SLEEP → FORGET → CONSOLIDATE → WAKE → ↺
"""

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
# New modules (feedback priorities)
from src.chetnaos.organism.founder_context    import FounderContext
from src.chetnaos.organism.simulation         import SimulationEngine
from src.chetnaos.organism.meta_cognition     import MetaCognition

from .state_machine import StateMachine, CycleStage
from .sleep_manager import SleepManager
from .llm_router    import LLMRouter


class CognitiveCycle:
    """
    The main orchestrator of all cognitive stages.
    One instance lives for the lifetime of the application.
    """

    def __init__(self):
        # Orchestrator
        self.llm      = LLMRouter()
        self.sm       = StateMachine()
        self.sleeper  = SleepManager()

        # Organism modules
        self.existence      = Existence()
        self.purpose        = Purpose()
        self.perception     = Perception()
        self.attention      = Attention()
        self.memory         = Memory()
        self.imagination    = Imagination()
        self.play_mod       = Play()
        self.abstraction    = Abstraction()
        self.world          = WorldModel()
        self.reasoning      = Reasoning()
        self.planning       = Planning()
        self.decision       = Decision()
        self.embodiment     = Embodiment()
        self.habit          = Habit()
        self.experience     = Experience()
        self.reality        = RealityChecker()
        self.reflection     = Reflection()
        self.learning       = Learning()
        self.beliefs        = Beliefs()
        self.identity       = Identity()
        self.development    = Development()
        self.homeostasis    = Homeostasis()
        self.sleep_mod      = Sleep()
        self.relationship   = Relationship()
        self.artifacts      = Artifacts()
        self.civ_memory     = CivilizationMemory()
        # New modules
        self.founder_ctx    = FounderContext()
        self.simulation     = SimulationEngine()
        self.meta_cog       = MetaCognition()

    def run(self, user_input: str, mode: str = "chat") -> dict:
        """Execute the full cognitive cycle for one input."""
        trace: list[dict] = []

        def step(stage: CycleStage, result: dict):
            self.sm.advance(stage)
            trace.append({"stage": stage.value,
                          **{k: v for k, v in result.items() if k != "stage"}})
            return result

        # ── EXIST ──────────────────────────────────────────────────
        exist_r = step(CycleStage.EXIST, self.existence.pulse())
        cycle_n = exist_r["cycle"]

        # ── PURPOSE ────────────────────────────────────────────────
        purpose_r = step(CycleStage.PURPOSE, self.purpose.get())

        # ── OBSERVE (Perception) ───────────────────────────────────
        percept = self.perception.perceive(user_input)
        step(CycleStage.OBSERVE, percept)

        # ── ATTEND ─────────────────────────────────────────────────
        att = self.attention.attend(percept)
        step(CycleStage.ATTEND, att)

        # ── RECALL ─────────────────────────────────────────────────
        recalled = self.memory.recall(user_input, k=4)
        founder_ctx_str = self.founder_ctx.get_system_context()
        step(CycleStage.RECALL, {
            "recalled_count": len(recalled),
            "items": recalled[:2],
            "founder_context_loaded": True,
        })

        # ── PREDICT (abstraction as prediction context) ─────────────
        abstr = self.abstraction.abstract(percept, att)
        step(CycleStage.PREDICT, {**abstr, "domain": abstr["domain"]})

        # ── IMAGINE ────────────────────────────────────────────────
        use_llm = abstr["complexity"] == "complex"
        imag = self.imagination.imagine(att, self.llm if use_llm else None)
        step(CycleStage.IMAGINE, imag)

        # ── PLAY ───────────────────────────────────────────────────
        play_r = self.play_mod.explore(att, imag)
        step(CycleStage.PLAY, play_r)

        # ── PLAN (+ Simulation sub-step) ───────────────────────────
        plan_r  = self.planning.plan(play_r, abstr, self.llm if use_llm else None)
        # Simulation Engine: generate Plan A / B / C
        sim_r   = self.simulation.simulate(plan_r["plan"], abstr,
                                           self.llm if use_llm else None)
        selected_plan = sim_r["selected"]
        step(CycleStage.PLAN, {**plan_r, "simulation": sim_r})

        # ── DECIDE (pre-reason habit check) ────────────────────────
        habit_r = self.habit.check(percept["intent"], abstr["domain"])
        step(CycleStage.HABIT, habit_r)

        # ── ACT (REASON — primary LLM call) ────────────────────────
        reason_r = self.reasoning.reason(
            user_input, recalled, selected_plan,
            self.llm, founder_context=founder_ctx_str
        )
        raw_response = reason_r["response"]
        step(CycleStage.ACT, reason_r)

        # ── WORLD UPDATE ───────────────────────────────────────────
        world_r = self.world.update(att, abstr)
        step(CycleStage.WORLD_UPDATE, world_r)

        # ── EXPERIENCE ─────────────────────────────────────────────
        exp_r = self.experience.record({
            "input":       user_input,
            "output":      raw_response,
            "domain":      abstr["domain"],
            "cycle_count": cycle_n,
            "confidence":  0.6,
        })
        step(CycleStage.EXPERIENCE, exp_r)

        # ── REALITY CHECK (+ feasibility) ──────────────────────────
        reality_r = self.reality.check(raw_response, {
            "beliefs": self.beliefs.get_all(),
        })
        step(CycleStage.REALITY_CHECK, reality_r)

        # ── EVALUATE (DECIDE) ──────────────────────────────────────
        dec_r = self.decision.decide(reason_r, reality_r)
        step(CycleStage.EVALUATE, dec_r)

        # ── FAILURE RECOVERY ───────────────────────────────────────
        final_output = dec_r["final"]
        step(CycleStage.FAILURE_RECOVERY, {
            "recovered": False,
            "output":    final_output,
        })

        # ── REFLECT ────────────────────────────────────────────────
        reflect_r = self.reflection.reflect(dec_r, reality_r, {
            "intent":     percept["intent"],
            "risk_level": "low",
        })
        step(CycleStage.REFLECT, reflect_r)

        # ── SELF QUESTION + META-COGNITION ─────────────────────────
        meta_r = self.meta_cog.evaluate(percept, dec_r, reflect_r, reality_r)
        step(CycleStage.SELF_QUESTION, {
            "question":  f"Did I serve '{percept['intent']}' with truth and compassion?",
            "answer":    "yes" if reflect_r["quality"] in ("good", "fair") else "needs_improvement",
            "meta":      meta_r,
        })

        # ── UPDATE BELIEFS ─────────────────────────────────────────
        learn_r   = self.learning.learn(reflect_r, exp_r)
        beliefs_r = self.beliefs.update(reflect_r, learn_r)
        step(CycleStage.UPDATE_BELIEFS, beliefs_r)

        # ── UPDATE IDENTITY ────────────────────────────────────────
        identity_r = self.identity.update(reflect_r, beliefs_r)
        self.identity.tick()
        step(CycleStage.UPDATE_IDENTITY, identity_r)

        # ── REFINE PURPOSE ─────────────────────────────────────────
        if reflect_r["quality"] == "good":
            self.purpose.refine(
                f"Handled {abstr['domain']} {percept['intent']} well "
                f"(dharma={reflect_r['dharma_score']})."
            )
        step(CycleStage.REFINE_PURPOSE, self.purpose.get())

        # ── SLEEP / FORGET / CONSOLIDATE / WAKE ────────────────────
        slept = False
        if self.sleeper.should_sleep(cycle_n):
            sleep_r = self.sleep_mod.consolidate(self.beliefs, self.memory, cycle_n)
            step(CycleStage.SLEEP,       sleep_r)
            step(CycleStage.FORGET,      {"forgotten": sleep_r.get("forgotten", 0)})
            step(CycleStage.CONSOLIDATE, {"consolidated": sleep_r.get("consolidated", 0)})
            step(CycleStage.WAKE,        self.sleep_mod.wake())
            self.sleeper.mark_slept(cycle_n)
            slept = True
        else:
            step(CycleStage.SLEEP,       {"slept": False,
                                           "next_in": self.sleeper.cycles_until_sleep(cycle_n)})
            step(CycleStage.FORGET,      {"forgotten": 0})
            step(CycleStage.CONSOLIDATE, {"consolidated": 0})
            step(CycleStage.WAKE,        {"refreshed": True})

        # Development + homeostasis + side effects
        dev_r  = self.development.record(reflect_r, reality_r["confidence"])
        home_r = self.homeostasis.check(dev_r, reflect_r)

        self.habit.record(percept["intent"], abstr["domain"])
        self.relationship.update("user")
        self.artifacts.store(final_output, abstr["domain"], percept["intent"])
        civ_r = self.civ_memory.contribute(
            reflect_r["cycle_score"], final_output, abstr["domain"]
        )
        self.memory.store("interaction",
                          f"Q: {user_input[:200]}\nA: {final_output[:300]}")

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
            "simulation":       sim_r,
            "meta_cognition": {
                "why":          meta_r["why"],
                "was_correct":  meta_r["was_correct"],
                "correctness":  meta_r["correctness"],
                "can_improve":  meta_r["can_improve"],
                "self_verdict": meta_r["self_verdict"],
            },
            "trace": trace,
        }
