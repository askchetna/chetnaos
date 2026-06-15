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
from src.chetnaos.cognition.executive import ExecutiveController
from src.chetnaos.cognition.self_model import SelfModel
from src.chetnaos.cognition.curiosity import CuriosityDrive
from src.chetnaos.cognition.emotion import EmotionalState
from src.chetnaos.cognition.goal_manager import GoalManager, GoalType
from src.chetnaos.memory.working_memory import WorkingMemory


class CognitiveCycle:
    def __init__(self):
        # Orchestrator
        self.llm     = LLMRouter()
        self.sm      = StateMachine()
        self.sleeper = SleepManager()
        self.executive = ExecutiveController(sleep_manager=self.sleeper)

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

        # Cognitive organs (Phase 3c — signal providers)
        self.working_memory = WorkingMemory(hierarchy=self.mem_hierarchy)
        self.self_model     = SelfModel()
        self.curiosity      = CuriosityDrive()
        self.emotion        = EmotionalState()
        self.goal_manager   = GoalManager()

        # In-memory session state
        self._recent_reality_checks: deque = deque(maxlen=8)
        self._last_sim          = {}
        self._last_meta         = {}
        self._last_thought_birth = {}
        self._last_sleep_data   = {}
        self._training_goals    = self.self_trainer.get()
        self._last_cognitive_signals: dict = {}

    # ──────────────────────────────────────────────────────────────────────
    def run(self, user_input: str, mode: str = "chat") -> dict:
        trace: list[dict] = []
        self.executive.reset_cycle_context(mode=mode, user_input=user_input)

        def step(stage: CycleStage, result: dict):
            self.executive.before_stage(stage, self.executive.context)
            if not self.executive.should_run(stage, self.executive.context):
                return result
            self.sm.advance(stage)
            trace.append({"stage": stage.value,
                          **{k: v for k, v in result.items() if k != "stage"}})
            self.executive.after_stage(stage, result, self.executive.context)
            return result

        # ── EXIST ──────────────────────────────────────────────────────
        exist_r = step(CycleStage.EXIST, self.existence.pulse())
        cycle_n = exist_r["cycle"]
        self.executive.update_context(cycle_n=cycle_n)

        # ── PURPOSE ────────────────────────────────────────────────────
        purpose_r = step(CycleStage.PURPOSE, self.purpose.get())
        if mode == "goal" and user_input.strip():
            self.goal_manager.add_goal(
                user_input.strip(),
                goal_type=GoalType.USER,
                priority=90.0,
                origin="api_goal",
            )

        # ── OBSERVE ────────────────────────────────────────────────────
        percept = self.perception.perceive(user_input)
        step(CycleStage.OBSERVE, percept)

        # ── ATTEND ─────────────────────────────────────────────────────
        att = self.attention.attend(percept)
        step(CycleStage.ATTEND, att)
        att_weight = {"HIGH": 1.0, "MEDIUM": 0.7, "NORMAL": 0.5}.get(att.get("priority"), 0.5)
        self.working_memory.push({
            "input": user_input[:100], "intent": percept.get("intent"),
        }, attention_weight=att_weight)

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
        self.executive.update_context(
            complexity=abstr.get("complexity", "simple"),
            domain=abstr.get("domain", "general"),
        )
        self.mem_hierarchy.add_semantic(abstr.get("domain", "general"))

        # ── IMAGINE ────────────────────────────────────────────────────
        imag = self.imagination.imagine(
            att, self.executive.llm_router_for(CycleStage.IMAGINE, self.llm),
        )
        step(CycleStage.IMAGINE, imag)

        # ── PLAY ───────────────────────────────────────────────────────
        play_r = self.play_mod.explore(att, imag)
        step(CycleStage.PLAY, play_r)

        # ── PLAN + SIMULATION ──────────────────────────────────────────
        plan_r = self.planning.plan(
            play_r, abstr, self.executive.llm_router_for(CycleStage.PLAN, self.llm),
        )
        sim_r  = self.simulation.simulate(
            plan_r["plan"], abstr,
            self.executive.llm_router_for(CycleStage.PLAN, self.llm),
        )
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

        # ── FAILURE RECOVERY / ACTION (embodiment) ───────────────────────
        emb_r = self.embodiment.act(dec_r, percept)
        final_output = emb_r["output"]
        step(CycleStage.FAILURE_RECOVERY, {
            "recovered": False,
            "output": final_output,
            "executed": emb_r.get("executed", True),
        })

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
            "answer":   self.executive.self_question_answer(reflect_r["quality"]),
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
        if self.executive.should_refine_purpose(reflect_r["quality"]):
            self.purpose.refine(
                f"Handled {abstr['domain']} {percept['intent']} well "
                f"(dharma={reflect_r['dharma_score']})."
            )
        step(CycleStage.REFINE_PURPOSE, self.purpose.get())

        # ── SLEEP / FORGET / CONSOLIDATE / WAKE ────────────────────────
        slept = False
        sleep_data = {}
        if self.executive.should_sleep_consolidation(cycle_n):
            sleep_r = self.sleep_mod.consolidate(self.beliefs, self.memory, cycle_n)
            step(CycleStage.SLEEP,       sleep_r)
            step(CycleStage.FORGET,      {"forgotten": sleep_r.get("forgotten", 0)})
            step(CycleStage.CONSOLIDATE, {"consolidated": sleep_r.get("consolidated", 0)})
            step(CycleStage.WAKE,        self.sleep_mod.wake())
            self.executive.mark_slept(cycle_n)
            self.mem_hierarchy.record_forgetting(sleep_r.get("forgotten", 0))
            slept = True
            sleep_data = sleep_r
            self._last_sleep_data = sleep_r
        else:
            next_in = self.executive.cycles_until_sleep(cycle_n)
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
        if self.executive.should_add_workspace_artifact(final_output):
            self.workspace.add_artifact(
                f"{abstr['domain']}_response_{cycle_n}.txt", "response"
            )

        # Memory hierarchy: add unsolved question if quality was poor
        if self.executive.should_poor_quality_followup(reflect_r["quality"]):
            self.workspace.add_question(f"Why did cycle {cycle_n} score poorly?")
            self.working_memory.add_dream(user_input[:80])

        # ── Cognitive organ signals (no pipeline change) ─────────────────
        ws = self.workspace.get()
        curiosity_goals = self.curiosity.exploration_goals(
            domain=abstr["domain"],
            workspace_questions=ws.get("unsolved_questions", []),
            uncertainty=1.0 - reality_r["confidence"],
            poor_quality=reflect_r["quality"] == "poor",
        )
        self._last_cognitive_signals = {
            "working_memory": self.working_memory.health(),
            "self_model": self.self_model.update(
                skills=self.skills.get_all(),
                development=self.development._data,
                meta_cognition=meta_r,
                reality_confidence=reality_r["confidence"],
            ),
            "curiosity": {
                **self.curiosity.snapshot(),
                "exploration_goals": curiosity_goals,
                "next_question": self.curiosity.next_question(
                    ws.get("unsolved_questions", []),
                ),
            },
            "emotion": self.emotion.update(
                reflection_quality=reflect_r["quality"],
                homeostasis_health=home_r["health"],
                attention_priority=att.get("priority", "NORMAL"),
                emotional_cue=att.get("emotional", False),
                reality_confidence=reality_r["confidence"],
            ),
        }
        self.goal_manager.ingest_signals(
            purpose=purpose_r.get("statement"),
            training_goals=self._training_goals,
            curiosity_goals=curiosity_goals,
            self_model_limits=self.self_model.known_limits(),
            founder_context=self.founder_ctx.get(),
        )
        if not self.goal_manager.active_goal():
            self.goal_manager.next_goal()
        self._last_cognitive_signals["goal_manager"] = {
            **self.goal_manager.goal_status(),
            "statistics": self.goal_manager.goal_statistics(),
        }

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
            "cognitive_organs": {
                "working_memory": self.working_memory.health(),
                "self_model":     self.self_model.snapshot(),
                "curiosity":      self.curiosity.snapshot(),
                "emotion":        self.emotion.snapshot(),
                "goal_manager":   {
                    **self.goal_manager.goal_status(),
                    "statistics": self.goal_manager.goal_statistics(),
                },
                "last_signals":   self._last_cognitive_signals,
            },
        }
