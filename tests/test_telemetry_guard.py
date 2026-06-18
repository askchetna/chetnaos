"""Telemetry narration guard tests."""
import unittest

from src.chetnaos.reasoning.honesty_guard import apply_telemetry_narration_guard


class TestTelemetryNarrationGuard(unittest.TestCase):
    def test_strips_organ_count_claims(self):
        text = "I activated 12 organs during this cycle."
        out, changes = apply_telemetry_narration_guard(text, {"cycle_id": "abc"})
        self.assertNotIn("12 organs", out)
        self.assertTrue(changes)

    def test_strips_cycle_duration_claims(self):
        text = "The cycle duration was 450ms overall."
        out, _ = apply_telemetry_narration_guard(text, {})
        self.assertNotIn("450ms", out)
        self.assertIn("Runtime Trace", out)

    def test_preserves_non_telemetry_prose(self):
        text = "The answer is 42 because of basic arithmetic."
        out, changes = apply_telemetry_narration_guard(text, {})
        self.assertEqual(out, text)
        self.assertEqual(changes, [])


if __name__ == "__main__":
    unittest.main()
