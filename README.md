# SD-WAN Controller: Python Policy Simulator

A runnable, dependency-free Python simulator for **flow-level path selection, bandwidth admission and recovery from link failures or service degradation**.

This is a new portfolio implementation using synthetic telemetry. It is separate from the author's doctoral implementation and published experiments. It does not configure routers, install routes, capture packets or implement an SD-WAN data plane.

## Quick start

Requires **Python 3.10 or later**. Run these commands from this repository's root. On Windows, use `py` in place of `python` if required.

```bash
python -m sdwan examples/failover.json --compare
python -m sdwan examples/failover.json --policy adaptive --output results/adaptive.json
python -m unittest discover -s tests -v
```

No third-party runtime packages, GNS3 installation or network permissions are required. An optional package installation with `python -m pip install .` exposes the equivalent `sdwan-sim` command. The package build uses setuptools; the commands above run directly without installation.

## What it demonstrates

- Admission control using reserved bandwidth on each WAN link.
- Hard per-flow limits for latency, jitter and loss.
- Three policies with identical eligibility checks: adaptive scoring, round-robin and static link priority.
- Recovery for active flows when a link fails or stops meeting their limits.
- Explicit rejection and drop decisions when no suitable path is available.
- JSON decision logs, per-tick link loads and aggregate service metrics.
- Unit and command-line tests, plus a GitHub Actions workflow.

## Included experiment

`examples/failover.json` defines 12 simulation ticks, three synthetic WAN links, and nine flows representing voice, video and backup traffic. Broadband fails at tick 4. Fibre latency rises at tick 7. Both recover at tick 9.

Run:

```bash
python -m sdwan examples/failover.json --compare --output results/comparison.json
```

The deterministic result is:

| Policy | Admitted | Rejected | Reroute events | Dropped | Completed | Service ratio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Adaptive | 8 | 1 | 2 | 3 | 5 | 0.717647 |
| Round-robin | 8 | 1 | 1 | 3 | 5 | 0.700000 |
| Static priority | 8 | 1 | 1 | 4 | 4 | 0.600000 |

`examples/expected_comparison.json` contains the full corresponding output. These are results of one deliberately small synthetic workload, not evidence of general superiority. A different workload, link order or set of weights may favour another policy.

The **service ratio** is the sum of reserved Mbps across served ticks divided by total requested Mbps across all requested durations. It includes rejected and subsequently dropped demand in the denominator. It is not measured throughput or a packet delivery ratio. An empty workload reports 1.0 by convention.

## Policy design

Every policy first excludes links that are down, lack capacity, or violate the flow's latency, jitter or loss limits.

| Policy | Selection among eligible links |
| --- | --- |
| `adaptive` | Lowest weighted score using projected utilisation, latency, jitter, loss and cost |
| `round_robin` | Next eligible link in a rotating input-order list |
| `static` | First eligible link in scenario input order, with fallback |

The adaptive score is:

```text
0.45 * projected_utilisation
+ 0.25 * latency_ms / 100
+ 0.10 * jitter_ms / 20
+ 0.15 * loss_pct / 1
+ 0.05 * cost / 10
```

Reference scales and weights are illustrative constants. They are neither trained nor tuned against real measurements. Values are not clipped to one. `cost` is a non-negative relative cost index, not a currency or financial charge. Equal adaptive scores are resolved by link name. Healthy flows stay on their paths; the controller does not continuously rebalance them.

## Scenario format

See [the scenario guide](docs/SCENARIOS.md) for fields, units, validation and tick ordering. All input is local JSON; the simulator performs no network calls.

## Source guide

| Path | Purpose |
| --- | --- |
| `sdwan/core.py` | Validated link/flow models, controller and simulation loop |
| `sdwan/__main__.py` | CLI, comparison table and JSON export |
| `tests/test_core.py` | Admission, recovery, validation and CLI tests |
| `examples/failover.json` | Synthetic workload and telemetry events |
| `examples/expected_comparison.json` | Reproducible output for all policies |
| `docs/SCENARIOS.md` | Schema, assumptions and execution semantics |
| `docs/VALIDATION.md` | Checks performed and scope of evidence |

## Limitations and extensions

This is a single-site, parallel-link model with fixed flow demand. It has no queues, congestion-dependent latency, TCP dynamics, packet scheduling, topology discovery or live telemetry collection. Recovery is instantaneous at tick boundaries with no switching penalty. Dropped or rejected flows are not retried. A flow that completes may previously have been rerouted.

Useful extensions include workload sweeps, sensitivity analysis of the scoring weights, recovery delays, and an explicitly separate adapter for a controlled network laboratory. A router or GNS3 integration would require additional implementation and validation.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Include a reproducible scenario with changes to scheduling or policy behaviour. Use synthetic data and exclude passwords, network credentials and personal data from contributions.

## Licence

MIT. See [LICENSE](LICENSE).
