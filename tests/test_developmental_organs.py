"""Tests for developmental cognitive organs."""
from src.chetnaos.organism.developmental_age import DevelopmentalAge
from src.chetnaos.organism.identity import Identity
from src.chetnaos.organism.relationship import Relationship, FOUNDER_DEFAULT
from src.chetnaos.organism.development import Development
from src.chetnaos.organism.value_organ import ValueOrgan
from src.chetnaos.organism.temporal_continuity import TemporalContinuity
from src.chetnaos.organism.reflection_organ import ReflectionOrgan
from src.chetnaos.reasoning.response_composer import ResponseComposer


def test_identity_defaults_include_chetna():
    assert Identity.DEFAULT["name"] == "Chetna"
    identity = Identity()
    data = identity.get()
    assert data["role"] == "Cognitive AI System"
    assert data["type"] == "Cognitive AI System"
    assert data["biological"] is False
    assert data["animal"] is False
    assert data["living_organism"] is False
    assert "identity_stability" in data
    assert data["identity_stability"] >= 0.7


def test_founder_relationship_preserved():
    rel = Relationship()
    founder = rel.founder()
    assert founder["name"] == FOUNDER_DEFAULT["name"]
    assert founder["role"] == "Founder"
    assert founder["relationship"] == "Creator"
    assert founder["attachment"] == "primary"


def test_development_traits_evolve_slowly():
    dev = Development()
    before = dict(dev._data["traits"])
    dev.record({"quality": "good"}, 0.85, domain="research")
    after = dev._data["traits"]
    assert after["reflection"] >= before["reflection"]
    assert after["research_maturity"] >= before["research_maturity"]


def test_developmental_age_from_quality_not_cycles():
    dev = {"total_cycles": 100, "good_cycles": 10, "poor_cycles": 80,
           "traits": {"curiosity": 0.3, "discipline": 0.3, "reflection": 0.3,
                      "creativity": 0.3, "consistency": 0.3, "wisdom": 0.3,
                      "research_maturity": 0.3}}
    id_data = {"identity_stability": 0.8}
    low = DevelopmentalAge.compute(dev, id_data)
    dev["good_cycles"] = 85
    dev["traits"] = {k: 0.85 for k in dev["traits"]}
    high = DevelopmentalAge.compute(dev, id_data)
    assert high["maturity_score"] > low["maturity_score"]
    assert high["stage"] != "Seed" or low["stage"] == "Seed"


def test_response_composer_strips_telemetry():
    raw = "Hello.\ncycle #42\nconfidence: 85%\nThere was no change detected."
    out = ResponseComposer.compose(raw)
    assert "cycle" not in out.lower() or "cycle" not in out
    assert "85%" not in out
    assert "Nothing major has changed" in out or "shift" in out.lower()


def test_temporal_continuity_tracks_today():
    tc = TemporalContinuity()
    tc.tick(user_input="test question", domain="business", quality="good", focus="launch")
    snap = tc.snapshot()
    assert snap["today_summary"]
    assert snap["last_session_at"]


def test_reflection_organ_records():
    ro = ReflectionOrgan()
    r = ro.from_cycle(domain="research", quality="good", meta_why="AGI architecture")
    assert r.get("recorded") is True
    assert len(ro.recent(1)) >= 1


def test_value_organ_priorities():
    vo = ValueOrgan()
    tops = vo.top_priorities(3)
    assert len(tops) == 3
    assert "truth" in tops or "growth" in tops
