import importlib.util
import os
import re
import unittest

APP_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py"
)


def load_app():
    spec = importlib.util.spec_from_file_location("cocotime_app", APP_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CocotimeTest(unittest.TestCase):
    def setUp(self):
        self.mod = load_app()
        self.client = self.mod.app.test_client()

    def test_index_ok(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        body = res.get_data(as_text=True)
        self.assertIn("cocotime", body)
        self.assertIn("時計", body)

    def test_all_panels_present(self):
        body = self.client.get("/").get_data(as_text=True)
        for panel in ("panel-clock", "panel-timer", "panel-stopwatch", "panel-calc"):
            self.assertIn(panel, body)
        for label in ("タイマー", "ストップウォッチ", "電卓"):
            self.assertIn(label, body)

    def test_clock_parts(self):
        body = self.client.get("/").get_data(as_text=True)
        self.assertIn('id="digital"', body)
        self.assertIn('id="analog"', body)
        self.assertIn('id="hourHand"', body)
        self.assertIn('id="cocoaLine"', body)

    def test_timer_parts(self):
        body = self.client.get("/").get_data(as_text=True)
        self.assertIn('id="timerDisplay"', body)
        self.assertIn('id="timerMin"', body)
        self.assertIn('id="timerSec"', body)
        self.assertIn('data-preset="1500"', body)
        self.assertIn(self.mod.TIMER_DONE_LINE, body)

    def test_calculator_no_eval(self):
        with open(APP_PATH, encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("eval(", source)
        body = self.client.get("/").get_data(as_text=True)
        self.assertIn('id="calcDisplay"', body)
        self.assertIn("calcApply", body)

    def test_greetings_cover(self):
        self.assertEqual(len(self.mod.GREETINGS), 5)
        self.assertEqual(len(self.mod.GREETINGS), len(set(self.mod.GREETINGS)))
        body = self.client.get("/").get_data(as_text=True)
        for line in self.mod.GREETINGS:
            self.assertIn(line, body)

    def test_healthz(self):
        res = self.client.get("/healthz")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), {"status": "ok", "app": "cocotime"})

    def test_not_found(self):
        res = self.client.get("/no-such-page")
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
