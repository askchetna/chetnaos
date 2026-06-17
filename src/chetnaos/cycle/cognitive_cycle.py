"""
Cognitive Cycle — The 27-stage locked cycle of ChetnaOS v2.0
Integrates: Simulation · MetaCognition · FounderContext ·
            Skills · WorkspaceState · ContradictionTracker · MemoryHierarchy
"""
import time
from collections import deque
from typing import Any

from src.chetnaos.organism.existence          import Existence
from src.chetnaos.organism.purpose            import Purpose
from src.chetnaos.organism.perception         import Perception
from src.chetnaos.organism.attention          import Attention
from src.chetnaos.organism.memory             import Memory
from src.chetnaos.organism.imagination        import Imagination
from src.chetnaos.organism.play               import Play
from src.chetnaos.organism.abstraction        import Abstraction
from src.chetnaos.organism.world_model        import WorldModel
from src.chetnaos.reasoning.reasoning          import Reasoning
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

from src.chetnaos.runtime.state_machine import StateMachine, CycleStage
from src.chetnaos.runtime.sleep_manager import SleepManager
from src.chetnaos.reasoning.llm_router import LLMRouter
from src.chetnaos.tools.agent_tools import run_agent_tool
from src.chetnaos.cognition.executive import ExecutiveController
from src.chetnaos.cognition.self_model import SelfModel
from src.chetnaos.cognition.curiosity import CuriosityDrive
from src.chetnaos.cognition.emotion import EmotionalState
from src.chetnaos.cognition.goal_manager import GoalManager, GoalType
from src.chetnaos.cognition.belief_revision import BeliefRevisionEngine
from src.chetnaos.memory.working_memory import WorkingMemory
from src.chetnaos.reasoning.context_builder import ContextBuilder
from src.chetnaos.cycle.cycle_trace import CycleTrace


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
        self.belief_revision = BeliefRevisionEngine()
        self.context_builder = ContextBuilder()

        # In-memory session state
        self._recent_reality_checks: deque = deque(maxlen=8)
        self._last_sim          = {}
        self._last_meta         = {}
        self._last_thought_birth = {}
        self._last_sleep_data   = {}
        self._training_goals    = self.self_trainer.get()
        self._last_cognitive_signals: dict = {}
        self._last_agent_tool: dict | None = None
        self._last_cycle_trace: list = []
        self._last_belief_changes: list = []
        self._last_contradiction_resolutions: list = []
        self._last_resolution_belief_changes: list = []
        self._last_memory_influence: list = []
        self._last_belief_influence: list = []
        self._last_memory_trace: dict = {}
        self._last_goal_progress: dict = {}

    def _build_reasoning_context(
        self,
        *,
        abstr: dict,
        att: dict,
        purpose_r: dict,
        mode: str,
        agent_tool: dict | None = None,
    ) -> dict:
        """Assemble lightweight organ context for the reasoning prompt."""
        ws = self.workspace.get()
        self.self_model.update(
            skills=self.skills.get_all(),
            development=self.development._data,
        )
        curiosity_goals = self.curiosity.exploration_goals(
            domain=abstr.get("domain", "general"),
            workspace_questions=ws.get("unsolved_questions", []),
            uncertainty=0.5,
            poor_quality=False,
        )
        self.goal_manager.ingest_signals(
            purpose=purpose_r.get("statement"),
            training_goals=self._training_goals,
            curiosity_goals=curiosity_goals,
            self_model_limits=self.self_model.known_limits(),
            founder_context=self.founder_ctx.get(),
        )
        if not self.goal_manager.active_goal():
            self.goal_manager.next_goal()

        pre_emotion = self.emotion.update(
            reflection_quality="fair",
            homeostasis_health=self.homeostasis.check(
                {"stats": self.development._data}, {"quality": "fair"}
            )["health"],
            attention_priority=att.get("priority", "NORMAL"),
            emotional_cue=att.get("emotional", False),
            reality_confidence=0.5,
        )

        return self.context_builder.build(
            working_memory=self.working_memory.recall(),
            active_goal=self.goal_manager.active_goal(),
            beliefs=self.beliefs.get_all()[:5],
            self_model=self.self_model.snapshot(),
            curiosity={
                "novelty_score": self.curiosity.snapshot().get("novelty_score"),
                "exploration_goals": curiosity_goals,
            },
            emotion=pre_emotion,
            agent_tool=agent_tool,
        )

    def _runtime_inspection_snapshot(self) -> dict:
        """Lightweight organ state for API meta (not full dashboard)."""
        return {
            "working_memory": self.working_memory.health(),
            "self_model": self.self_model.snapshot(),
            "curiosity": self.curiosity.snapshot(),
            "emotion": self.emotion.snapshot(),
            "goal_manager": {
                **self.goal_manager.goal_status(),
                "statistics": self.goal_manager.goal_statistics(),
            },
            "belief_revision": self.belief_revision.snapshot(),
            "last_agent_tool": self._last_agent_tool,
            "last_cycle_trace": self._last_cycle_trace[-26:],
        }

    # ──────────────────────────────────────────────────────────────────────
    def run(self, user_input: str, mode: str = "chat", conversation_context: dict | None = None) -> dict:
        trace: list[dict] = []
        cycle_trace = CycleTrace()
        self.executive.reset_cycle_context(mode=mode, user_input=user_input)

        def step(
            stage: CycleStage,
            result: dict,
            *,
            stage_input: Any = None,
            memory_used: bool = False,
            beliefs_used: bool = False,
            goal_used: bool = False,
            plan_used: bool = False,
            confidence: float | None = None,
        ):
            t0 = time.perf_counter()
            self.executive.before_stage(stage, self.executive.context)
            if not self.executive.should_run(stage, self.executive.context):
                return result
            self.sm.advance(stage)
            trace.append({"stage": stage.value,
                          **{k: v for k, v in result.items() if k != "stage"}})
            self.executive.after_stage(stage, result, self.executive.context)
            duration_ms = (time.perf_counter() - t0) * 1000
            cycle_trace.record(
                stage.value,
                input_data=stage_input if stage_input is not None else user_input,
                output={k: v for k, v in result.items() if k != "stage"},
                confidence=confidence if confidence is not None else result.get("confidence"),
                duration_ms=duration_ms,
                memory_used=memory_used,
                beliefs_used=beliefs_used,
                goal_used=goal_used,
                plan_used=plan_used,
            )
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
        search_trace = self.memory.last_trace()
        founder_ctx_str = self.founder_ctx.get_system_context()
        step(CycleStage.RECALL, {
            "recalled_count": len(recalled),
            "founder_context_loaded": True,
            "search_method": search_trace.get("search_method"),
            "failure_point": search_trace.get("failure_point"),
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

        # ── Agent tools (organism path, not parallel LLM) ────────────────
        agent_tool = None
        if mode == "agent":
            agent_tool = run_agent_tool(user_input, llm_router=self.llm)
            self._last_agent_tool = agent_tool

        cognitive_ctx = self._build_reasoning_context(
            abstr=abstr,
            att=att,
            purpose_r=purpose_r,
            mode=mode,
            agent_tool=agent_tool,
        )

        # ── ACT (primary LLM call) ─────────────────────────────────────
        reason_r = self.reasoning.reason(
            user_input,
            recalled,
            selected_plan,
            self.llm,
            founder_context=founder_ctx_str,
            cognitive_context=cognitive_ctx,
            conversation_context=conversation_context,
        )
        raw_response = reason_r["response"]
        self._last_memory_influence = reason_r.get("memory_influence", [])
        self._last_belief_influence = reason_r.get("belief_influence", [])

        def _trace_row(m: dict) -> dict:
            return {
                "id": m.get("id"),
                "text": (m.get("text") or str(m))[:200],
                "score": m.get("score"),
                "source": m.get("source", "recall"),
                "method": m.get("method"),
            }

        injected = recalled[:3]
        self._last_memory_trace = {
            **search_trace,
            "memories_injected": [_trace_row(m) for m in injected],
            "memories_used": list(self._last_memory_influence),
            "injected_count": len(injected),
            "used_count": len(self._last_memory_influence),
            "reached_reasoning": len(recalled) > 0,
            "reached_prompt": len(injected) > 0,
            "memory_influence_nonempty": len(self._last_memory_influence) > 0,
        }
        step(
            CycleStage.ACT,
            reason_r,
            memory_used=bool(recalled),
            beliefs_used=reason_r.get("used_beliefs", False),
            goal_used=reason_r.get("used_active_goal", False),
            plan_used=reason_r.get("used_plan", False),
        )

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

        # ── DECIDE ─────────────────────────────────────────────────────
        dec_r = self.decision.decide(reason_r, reality_r)
        step(
            CycleStage.DECIDE,
            dec_r,
            confidence=dec_r.get("confidence"),
            memory_used=bool(recalled),
            beliefs_used=reason_r.get("used_beliefs", False),
            goal_used=reason_r.get("used_active_goal", False),
            plan_used=reason_r.get("used_plan", False),
        )

        # ── Embodiment (motor output — robotics/API actions future path) ─
        emb_r = self.embodiment.act(dec_r, percept)
        final_output = emb_r["output"]

        # ── EVALUATE ───────────────────────────────────────────────────
        eval_r = {
            "stage": "EVALUATE",
            "confidence": dec_r.get("confidence", reality_r["confidence"]),
            "caveat": dec_r.get("caveat", False),
            "passed": reality_r.get("passed", True),
            "belief_valid": reality_r.get("belief_valid", True),
        }
        step(CycleStage.EVALUATE, eval_r, confidence=eval_r.get("confidence"))

        # ── FAILURE RECOVERY ───────────────────────────────────────────
        step(CycleStage.FAILURE_RECOVERY, {
            "recovered": False,
            "output": final_output,
        })

        # ── REFLECT ────────────────────────────────────────────────────
        reflect_r = self.reflection.reflect(dec_r, reality_r, {
            "intent": percept["intent"], "risk_level": "low",
        })
        step(CycleStage.REFLECT, reflect_r)

        # ── Goal progress: prediction error ↔ corrective action loop ─────
        progress_r = self.goal_manager.update_prediction_error_loop(
            cycle_id=cycle_trace.cycle_id,
            cycle_n=cycle_n,
            reality=reality_r,
            reflection=reflect_r,
            evaluation=eval_r,
            decision=dec_r,
            goal_used=reason_r.get("used_active_goal", False),
            user_input=user_input,
            plan=selected_plan,
        )
        self._last_goal_progress = progress_r

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
        contradiction_resolutions = self.contradictions.resolve(self.beliefs.get_all())
        resolution_belief_changes: list = []
        for res in contradiction_resolutions:
            change = self.beliefs.weaken_by_text(
                res.get("weaker_belief", ""),
                delta=-0.06,
                reason=res.get("reason", "contradiction_resolution"),
            )
            if change:
                resolution_belief_changes.append(change)
        self.workspace.set_contradictions(self.contradictions.count())

        # ── Cognitive organs: GoalManager + BeliefRevision (signal only) ──
        self.goal_manager.ingest_signals(
            purpose=purpose_r.get("statement"),
            training_goals=self._training_goals,
            curiosity_goals=self.curiosity.exploration_goals(
                domain=abstr["domain"],
                workspace_questions=self.workspace.get().get("unsolved_questions", []),
                uncertainty=1.0 - reality_r["confidence"],
                poor_quality=reflect_r["quality"] == "poor",
            ),
            self_model_limits=self.self_model.known_limits(),
            founder_context=self.founder_ctx.get(),
        )
        if not self.goal_manager.active_goal():
            self.goal_manager.next_goal()

        self.belief_revision.observe(
            beliefs=self.beliefs.get_all(),
            reality=reality_r,
            reflection=reflect_r,
            learning=learn_r,
            goal_manager=self.goal_manager.goal_status(),
            self_model={"self_confidence": self.self_model.self_confidence()},
            memory_recalled=len(recalled),
            external_contradictions=self.contradictions.get(),
        )
        self.belief_revision.evaluate()
        revise_r = self.belief_revision.revise(self.beliefs)
        self._last_belief_changes = revise_r.get("belief_changes", [])
        self._last_contradiction_resolutions = contradiction_resolutions
        self._last_resolution_belief_changes = resolution_belief_changes

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

        # ── SLEEP / CONSOLIDATE / FORGET / WAKE ────────────────────────
        slept = False
        sleep_data = {}
        if self.executive.should_sleep_consolidation(cycle_n):
            sleep_r = self.sleep_mod.consolidate(self.beliefs, self.memory, cycle_n)
            step(CycleStage.SLEEP,       sleep_r)
            step(CycleStage.CONSOLIDATE, {"consolidated": sleep_r.get("consolidated", 0)})
            step(CycleStage.FORGET,      {"forgotten": sleep_r.get("forgotten", 0)})
            step(CycleStage.WAKE,        self.sleep_mod.wake())
            self.executive.mark_slept(cycle_n)
            self.mem_hierarchy.record_forgetting(sleep_r.get("forgotten", 0))
            slept = True
            sleep_data = sleep_r
            self._last_sleep_data = sleep_r
        else:
            next_in = self.executive.cycles_until_sleep(cycle_n)
            step(CycleStage.SLEEP,       {"slept": False, "next_in": next_in})
            step(CycleStage.CONSOLIDATE, {"consolidated": 0})
            step(CycleStage.FORGET,      {"forgotten": 0})
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
        self._last_cognitive_signals["goal_manager"] = {
            **self.goal_manager.goal_status(),
            "statistics": self.goal_manager.goal_statistics(),
        }
        self._last_cognitive_signals["belief_revision"] = self.belief_revision.snapshot()

        self.sm.complete_cycle()
        self._last_cycle_trace = cycle_trace.to_list()

        return {
            "reply":            final_output,
            "cycle":            cycle_n,
            "cycle_id":         cycle_trace.cycle_id,
            "stage_trace":      [t["stage"] for t in trace],
            "cycle_trace":      cycle_trace.to_list(),
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
            "cognitive_organs": self._runtime_inspection_snapshot(),
            "agent_tool": self._last_agent_tool.get("tool") if self._last_agent_tool else None,
            "reasoning_integration": {
                "used_working_memory": reason_r.get("used_working_memory", False),
                "used_active_goal": reason_r.get("used_active_goal", False),
                "used_beliefs": reason_r.get("used_beliefs", False),
                "used_conversation_context": reason_r.get("used_conversation_context", False),
                "used_cognitive_organs": reason_r.get("used_cognitive_organs", False),
                "used_agent_tool": reason_r.get("used_agent_tool", False),
                "memory_influence": self._last_memory_influence,
                "belief_influence": self._last_belief_influence,
            },
            "belief_changes": self._last_belief_changes,
            "contradiction_resolutions": self._last_contradiction_resolutions,
            "resolution_belief_changes": self._last_resolution_belief_changes,
            "goal_progress": self._last_goal_progress,
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
            "memory_influence": self._last_memory_influence,
            "belief_influence": self._last_belief_influence,
            "memory_trace": self._last_memory_trace,
            "goal_progress": self._last_goal_progress or self.goal_manager.goal_progress_summary(),
            "belief_changes": self._last_belief_changes,
            "contradiction_resolutions": self.contradictions.resolution_history()[:10],
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
                "belief_revision": self.belief_revision.snapshot(),
                "last_signals":   self._last_cognitive_signals,
                "last_cycle_trace": self._last_cycle_trace[-26:],
            },
        }
