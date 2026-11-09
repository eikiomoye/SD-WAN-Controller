# Scenarios and simulation semantics

The top-level JSON object must contain exactly `ticks`, `links`, `flows` and `events`.

## Fields

| Object | Required fields | Meaning |
| --- | --- | --- |
| Scenario | `ticks` | Positive integer horizon; one tick is an abstract time interval |
| Link | `name`, `capacity_mbps`, `latency_ms`, `jitter_ms`, `loss_pct`, `cost` | Unique name, positive bandwidth capacity, non-negative latency/jitter, loss percentage 0 to 100, non-negative relative cost |
| Link | optional `up` | Boolean availability, defaults to `true` |
| Flow | `id`, `arrival`, `duration`, `demand_mbps`, `max_latency_ms`, `max_jitter_ms`, `max_loss_pct` | Unique identifier, non-negative integer arrival, positive integer duration, positive fixed demand, non-negative delay limits, loss limit 0 to 100 |
| Event | `tick`, `link`, `changes` | Non-negative integer tick within the horizon, existing link name, non-empty object of telemetry changes |

`links`, `flows` and `events` are arrays. Links must be non-empty. Flows and events may be empty. All numeric values must be finite; booleans do not count as numbers. Arrival plus duration must be no greater than `ticks`, ensuring every admitted flow either completes or drops within the simulation. Capacity and demand have a minimum accepted value of 0.000001 Mbps. Capacity comparisons permit 1e-9 Mbps numerical tolerance.

Events can update only `latency_ms`, `jitter_ms`, `loss_pct` and `up`. Names, capacity and cost are fixed for a run. Only one event per link per tick is allowed. Event arrays may be unordered; events apply at their own ticks.

## Minimal example

```json
{
  "ticks": 3,
  "links": [
    {"name": "wan1", "capacity_mbps": 20, "latency_ms": 15,
     "jitter_ms": 2, "loss_pct": 0.1, "cost": 1}
  ],
  "flows": [
    {"id": "voice", "arrival": 0, "duration": 3, "demand_mbps": 2,
     "max_latency_ms": 40, "max_jitter_ms": 10, "max_loss_pct": 1}
  ],
  "events": []
}
```

## Per-tick order

1. Release all flows whose arrival plus duration has been reached.
2. Apply all telemetry events for the current tick.
3. Remove every active flow whose assigned link is down or breaches its limits.
4. Attempt recovery of those flows, in current reservation order.
5. Admit newly arriving flows in scenario input order.
6. Record reservations and accumulate served Mbps-ticks.

A final completion-only boundary is processed at `ticks`. For example, a flow arriving at tick 0 with duration 2 consumes bandwidth during ticks 0 and 1, then completes at tick 2 before new admissions.

Recovery retains the original completion time. Recovered flows receive first access to available capacity before new traffic. If recovery fails, the flow drops permanently. Newly rejected flows are also not retried. Recovery to a restored link is possible for future admissions, but already dropped flows stay dropped.

The order of simultaneous flows can affect admission outcomes. No policy uses future events or future flow arrivals. Each policy comparison starts from independent, empty reservations on the same input.

## Output

JSON export is always an array: one result with `--policy`, or three results with `--compare`. Each result has `policy`, `summary`, `decisions` and `snapshots`.

Decision actions are `admitted`, `rejected`, `rerouted`, `dropped` and `completed`. `link` is null for rejection and drop events. Reroute counts measure events, so one flow may contribute multiple reroutes. Snapshot `load_mbps` values are rounded to six decimals for readability; aggregate service calculations use unrounded reservations.

`requested_mbps_ticks` includes all requested durations. `served_mbps_ticks` includes only admitted service before completion or drop. Latency, jitter and loss are eligibility metadata; they do not reduce served volume in this model.
