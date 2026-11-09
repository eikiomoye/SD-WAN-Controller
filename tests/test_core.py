import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from sdwan.core import Controller, Flow, Link, simulate


def link(name="a", capacity=10, **kw):
    return Link(name, capacity, kw.get("latency", 10), 1, 0, kw.get("cost", 1), kw.get("up", True))


def flow(id="f", arrival=0, duration=2, demand=5):
    return Flow(id, arrival, duration, demand, 50, 10, 1)


def scenario():
    from dataclasses import asdict
    return {"ticks": 4, "links": [asdict(link()), asdict(link("b"))],
            "flows": [asdict(flow())], "events": []}


class ControllerTests(unittest.TestCase):
    def test_capacity_is_reserved_and_overbooking_rejected(self):
        c = Controller([link()])
        self.assertEqual(c.admit(flow(demand=10)), "a")
        self.assertIsNone(c.admit(flow("extra", demand=1)))
        self.assertEqual(c.used("a"), 10)

    def test_hard_slo_and_down_filter(self):
        c = Controller([link("slow", latency=80), link("down", up=False)])
        self.assertIsNone(c.admit(flow()))

    def test_adaptive_chooses_lower_projected_utilisation(self):
        c = Controller([link("small", capacity=5), link("large", capacity=100)])
        self.assertEqual(c.admit(flow()), "large")

    def test_adaptive_ties_use_link_name(self):
        c = Controller([link("z"), link("a")])
        self.assertEqual(c.admit(flow()), "a")

    def test_round_robin_rotates_and_static_uses_input_order(self):
        c = Controller([link(), link("b")], "round_robin")
        self.assertEqual([c.admit(flow(str(i), demand=1)) for i in range(3)], ["a", "b", "a"])
        c = Controller([link(), link("b")], "static")
        self.assertEqual([c.admit(flow(str(i), demand=1)) for i in range(3)], ["a"] * 3)

    def test_round_robin_skips_ineligible_links(self):
        c = Controller([link(up=False), link("b")], "round_robin")
        self.assertEqual(c.admit(flow()), "b")

    def test_duplicate_active_flow_rejected(self):
        c = Controller([link()])
        c.admit(flow())
        with self.assertRaises(ValueError):
            c.admit(flow())


class SimulationTests(unittest.TestCase):
    def test_release_before_new_admission(self):
        s = scenario()
        s["links"] = s["links"][:1]
        from dataclasses import asdict
        s["flows"] = [asdict(flow(demand=10)), asdict(flow("new", arrival=2, demand=10))]
        result = simulate(s)
        self.assertEqual(result["summary"]["admitted"], 2)
        self.assertEqual(result["summary"]["completed"], 2)
        self.assertEqual(result["summary"]["service_ratio"], 1)

    def test_failure_reroutes_without_resetting_duration(self):
        s = scenario()
        s["events"] = [{"tick": 1, "link": "a", "changes": {"up": False}}]
        result = simulate(s, "static")
        self.assertEqual(result["summary"]["rerouted"], 1)
        self.assertEqual(result["summary"]["completed"], 1)
        self.assertEqual(result["snapshots"][1]["load_mbps"], {"a": 0, "b": 5})
        self.assertEqual(result["decisions"][-1]["tick"], 2)

    def test_failure_without_alternative_drops_flow(self):
        s = scenario()
        s["links"] = s["links"][:1]
        s["events"] = [{"tick": 1, "link": "a", "changes": {"up": False}}]
        result = simulate(s)
        self.assertEqual(result["summary"]["dropped"], 1)
        self.assertEqual(result["summary"]["completed"], 0)
        self.assertEqual(result["summary"]["service_ratio"], .5)

    def test_slo_degradation_also_triggers_recovery(self):
        s = scenario()
        s["events"] = [{"tick": 1, "link": "a", "changes": {"latency_ms": 100}}]
        self.assertEqual(simulate(s, "static")["summary"]["rerouted"], 1)

    def test_rejected_flow_contributes_to_requested_service(self):
        s = scenario()
        s["flows"][0]["demand_mbps"] = 30
        result = simulate(s)
        self.assertEqual(result["summary"]["rejected"], 1)
        self.assertEqual(result["summary"]["service_ratio"], 0)

    def test_empty_workload(self):
        s = scenario()
        s["flows"] = []
        self.assertEqual(simulate(s)["summary"]["service_ratio"], 1)

    def test_simulation_deterministic_and_does_not_mutate_input(self):
        s = scenario()
        original = copy.deepcopy(s)
        self.assertEqual(simulate(s), simulate(s))
        self.assertEqual(s, original)

    def test_invalid_numeric_inputs(self):
        for value in (-1, float("nan"), float("inf"), True, "10"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                flow(demand=value)
        for value in (1.2, True, -1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                flow(arrival=value)

    def test_invalid_scenario_structures(self):
        variants = []
        s = scenario(); s["flows"] *= 2; variants.append(s)
        s = scenario(); s["links"] *= 2; variants.append(s)
        s = scenario(); s["flows"][0]["duration"] = 5; variants.append(s)
        s = scenario(); s["links"] = []; variants.append(s)
        s = scenario(); s["events"] = [{"tick": 1, "link": "missing", "changes": {"up": False}}]; variants.append(s)
        s = scenario(); s["events"] = [{"tick": 1, "link": "a", "changes": {"capacity_mbps": 1}}]; variants.append(s)
        s = scenario(); s["events"] = [{"tick": 1, "link": "a", "changes": {"up": "false"}}]; variants.append(s)
        s = scenario(); s["events"] = [{"tick": 1, "link": "a", "changes": {"up": False}}] * 2; variants.append(s)
        for s in variants:
            with self.subTest(s=s), self.assertRaises(ValueError):
                simulate(s)

    def test_demo_expected_outcomes_and_capacity_invariants(self):
        demo = json.loads(Path("examples/failover.json").read_text())
        expected = json.loads(Path("examples/expected_comparison.json").read_text())
        for index, policy in enumerate(Controller.POLICIES):
            result = simulate(demo, policy)
            self.assertEqual(result, expected[index])
            summary = result["summary"]
            self.assertEqual(summary["admitted"] + summary["rejected"], len(demo["flows"]))
            self.assertEqual(summary["completed"] + summary["dropped"], summary["admitted"])
            self.assertTrue(0 <= summary["service_ratio"] <= 1)
            capacity = {item["name"]: item["capacity_mbps"] for item in demo["links"]}
            for snapshot in result["snapshots"]:
                for assigned, load in snapshot["load_mbps"].items():
                    self.assertLessEqual(load, capacity[assigned])

    def test_cli_json_export_and_invalid_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "nested" / "result.json"
            run = subprocess.run([sys.executable, "-m", "sdwan", "examples/failover.json",
                                  "--compare", "--output", str(output)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(len(json.loads(output.read_text())), 3)
            bad = Path(directory) / "bad.json"
            bad.write_text('{"ticks": false}')
            run = subprocess.run([sys.executable, "-m", "sdwan", str(bad)], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertNotIn("Traceback", run.stderr)


if __name__ == "__main__":
    unittest.main()
