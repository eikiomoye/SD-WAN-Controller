# Validation record

Prepared on 9 November 2026.

## Executed checks

```bash
python -m unittest discover -s tests -v
python -m sdwan examples/failover.json --compare --output examples/expected_comparison.json
```

The test suite contains 18 passing tests covering capacity reservations, hard service constraints, deterministic tie behaviour and policy selection, duplicate flows, release ordering, link failure recovery, recovery without an alternative, telemetry degradation, rejected demand accounting, empty workloads, input validation, simulation repeatability, capacity invariants, exact example-output reproduction and command-line JSON export/errors.

The included example produced service ratios of 0.717647 (adaptive), 0.700000 (round-robin) and 0.600000 (static priority). The full results are committed as example output and can be regenerated. These are synthetic flow-reservation outcomes, not measured network throughput.

## Scope of evidence

Tests establish behaviour for the covered cases. They do not establish production suitability, statistical significance or performance on physical networks. No real routers, GNS3 systems, operating-system routing tables or remote services were exercised.

The workflow is configured to run on Python 3.10, 3.11, 3.12 and 3.13 after upload. Those remote CI runs have not yet taken place. The local validation interpreter is recorded in `LOCAL_VALIDATION.txt`.
