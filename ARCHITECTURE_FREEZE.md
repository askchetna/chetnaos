# ARCHITECTURE FREEZE — ChetnaOS v3
# Effective: 2026-06-16 (Guruji approval)
# Status: LOCKED until Phase 8 experiments complete

## DO NOT (without explicit founder approval)

- Add new cognitive **stages**
- Add new cognitive **organs**
- Add new **memory kernels** or parallel memory systems
- Add new **runtimes** or parallel agent paths
- Add new **identity systems**
- Add new **folders** for architecture
- Refactor cognitive cycle logic

## ALLOWED

- **7D2** shim removal (import fixes only, no logic changes)
- **Phase 8** runtime experiments (observe only)
- Bug fixes that preserve behavior (must pass all gates)
- Documentation and experiment reports

## Frozen organ list (28)

Perception · Attention · Memory · Prediction · Imagination · Play · Planning · Decision · Act · Habit · Experience · Reality · Evaluation · FailureRecovery · Reflection · SelfQuestion · Beliefs · Identity · Purpose · Sleep · Consolidate · Forget · Wake · Curiosity · Emotion · SelfModel · GoalManager · BeliefRevision

## Validation gates (mandatory after any change)

```powershell
python scripts/phase7_gate.py
python tests/test_runtime_validation.py
python tests/test_reasoning_integration.py
```

## Research thesis (defendable claim)

> ChetnaOS is a developmental cognitive architecture designed to study whether repeated interaction with the environment can gradually reshape memory, beliefs, identity, goals, and future behavior across multiple timescales.

## Next goal

**Runtime validation through long-duration experiments** — not new architecture.
