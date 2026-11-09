"""Run with python -m sdwan from the repository root."""

import argparse
import json
from pathlib import Path

from .core import Controller, simulate


def main():
    parser = argparse.ArgumentParser(description="Simulate SD-WAN flow admission and recovery")
    parser.add_argument("scenario", type=Path)
    parser.add_argument("--policy", choices=Controller.POLICIES, default="adaptive")
    parser.add_argument("--compare", action="store_true", help="run all three policies independently")
    parser.add_argument("--output", type=Path, help="save complete JSON decisions and metrics")
    args = parser.parse_args()
    try:
        data = json.loads(args.scenario.read_text(encoding="utf-8"))
        policies = Controller.POLICIES if args.compare else (args.policy,)
        results = [simulate(data, policy) for policy in policies]
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(results, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print("policy        admitted rejected rerouted dropped completed service_ratio")
    for result in results:
        summary = result["summary"]
        print(f"{result['policy']:13} {summary['admitted']:8} {summary['rejected']:8} "
              f"{summary['rerouted']:8} {summary['dropped']:7} {summary['completed']:9} "
              f"{summary['service_ratio']:13.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
