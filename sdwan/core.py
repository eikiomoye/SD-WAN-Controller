"""Flow-level admission and path selection using synthetic link telemetry."""

from dataclasses import dataclass, replace
import math


def number(value, label, minimum=0, maximum=None):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value < minimum
            or (maximum is not None and value > maximum)):
        raise ValueError(f"{label} must be finite and between {minimum} and {maximum}")
    return value


def integer(value, label, minimum=0):
    number(value, label, minimum)
    if not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    return value


def name(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


@dataclass(frozen=True)
class Link:
    name: str
    capacity_mbps: float
    latency_ms: float
    jitter_ms: float
    loss_pct: float
    cost: float
    up: bool = True

    def __post_init__(self):
        name(self.name, "link name")
        number(self.capacity_mbps, "capacity_mbps", minimum=0.000001)
        for field in ("latency_ms", "jitter_ms", "cost"):
            number(getattr(self, field), field)
        number(self.loss_pct, "loss_pct", maximum=100)
        if not isinstance(self.up, bool):
            raise ValueError("up must be a boolean")


@dataclass(frozen=True)
class Flow:
    id: str
    arrival: int
    duration: int
    demand_mbps: float
    max_latency_ms: float
    max_jitter_ms: float
    max_loss_pct: float

    def __post_init__(self):
        name(self.id, "flow id")
        integer(self.arrival, "arrival")
        integer(self.duration, "duration", 1)
        number(self.demand_mbps, "demand_mbps", minimum=0.000001)
        number(self.max_latency_ms, "max_latency_ms")
        number(self.max_jitter_ms, "max_jitter_ms")
        number(self.max_loss_pct, "max_loss_pct", maximum=100)

    @property
    def end(self):
        return self.arrival + self.duration


class Controller:
    """All policies share hard capacity and SLO filters for fair comparison."""

    POLICIES = ("adaptive", "round_robin", "static")

    def __init__(self, links, policy="adaptive"):
        if policy not in self.POLICIES:
            raise ValueError(f"policy must be one of {self.POLICIES}")
        self.links = {link.name: link for link in links}
        if not self.links or len(self.links) != len(links):
            raise ValueError("links must be non-empty with unique names")
        self.policy = policy
        self.active = {}  # flow id -> (Flow, link name)
        self.cursor = 0

    def used(self, link_name):
        return sum(f.demand_mbps for f, assigned in self.active.values()
                   if assigned == link_name)

    def eligible(self, flow, link):
        return (link.up and self.used(link.name) + flow.demand_mbps
                <= link.capacity_mbps + 1e-9
                and link.latency_ms <= flow.max_latency_ms
                and link.jitter_ms <= flow.max_jitter_ms
                and link.loss_pct <= flow.max_loss_pct)

    def score(self, flow, link):
        # Fixed reference scales, not measured or learned coefficients.
        return (0.45 * (self.used(link.name) + flow.demand_mbps) / link.capacity_mbps
                + 0.25 * link.latency_ms / 100
                + 0.10 * link.jitter_ms / 20
                + 0.15 * link.loss_pct / 1
                + 0.05 * link.cost / 10)

    def admit(self, flow):
        if flow.id in self.active:
            raise ValueError(f"active flow already exists: {flow.id}")
        links = list(self.links.values())
        if self.policy == "round_robin":
            indices = [(self.cursor + i) % len(links) for i in range(len(links))]
            candidates = [links[i] for i in indices if self.eligible(flow, links[i])]
        else:
            candidates = [link for link in links if self.eligible(flow, link)]
        if not candidates:
            return None
        selected = (min(candidates, key=lambda link: (self.score(flow, link), link.name))
                    if self.policy == "adaptive" else candidates[0])
        if self.policy == "round_robin":
            self.cursor = (links.index(selected) + 1) % len(links)
        self.active[flow.id] = (flow, selected.name)
        return selected.name


def load_scenario(data):
    """Validate the complete scenario before executing any steps."""
    if not isinstance(data, dict) or set(data) != {"ticks", "links", "flows", "events"}:
        raise ValueError("scenario requires exactly ticks, links, flows and events")
    ticks = integer(data["ticks"], "ticks", 1)
    for key in ("links", "flows", "events"):
        if not isinstance(data[key], list):
            raise ValueError(f"{key} must be a list")
    try:
        links = [Link(**item) for item in data["links"]]
        flows = [Flow(**item) for item in data["flows"]]
    except TypeError as exc:
        raise ValueError(f"invalid link or flow fields: {exc}") from exc
    controller = Controller(links)
    if len({f.id for f in flows}) != len(flows):
        raise ValueError("flow ids must be unique")
    if any(f.end > ticks for f in flows):
        raise ValueError("every flow must finish within ticks")
    seen = set()
    for event in data["events"]:
        if not isinstance(event, dict) or set(event) != {"tick", "link", "changes"}:
            raise ValueError("event requires exactly tick, link and changes")
        tick = integer(event["tick"], "event tick")
        if tick >= ticks or not isinstance(event["link"], str) or event["link"] not in controller.links:
            raise ValueError("event tick or link is invalid")
        changes = event["changes"]
        if (not isinstance(changes, dict) or not changes
                or not set(changes) <= {"latency_ms", "jitter_ms", "loss_pct", "up"}):
            raise ValueError("events may change latency_ms, jitter_ms, loss_pct or up")
        key = tick, event["link"]
        if key in seen:
            raise ValueError("only one event per link per tick is allowed")
        seen.add(key)
        replace(controller.links[event["link"]], **changes)
    return ticks, links, flows, data["events"]


def simulate(data, policy="adaptive"):
    ticks, links, flows, events = load_scenario(data)
    controller = Controller(links, policy)
    log, snapshots = [], []
    counters = dict(admitted=0, rejected=0, rerouted=0, dropped=0, completed=0)
    served = 0.0

    def record(tick, flow, action, link=None):
        log.append(dict(tick=tick, flow=flow.id, action=action, link=link))

    # Process the final boundary to report every completion.
    for tick in range(ticks + 1):
        for flow_id, (flow, assigned) in list(controller.active.items()):
            if flow.end <= tick:
                del controller.active[flow_id]
                counters["completed"] += 1
                record(tick, flow, "completed", assigned)
        if tick == ticks:
            break
        for event in events:
            if event["tick"] == tick:
                link_name = event["link"]
                controller.links[link_name] = replace(controller.links[link_name], **event["changes"])

        # Remove all affected reservations before choosing replacement paths.
        affected = []
        for flow_id, (flow, assigned) in list(controller.active.items()):
            link = controller.links[assigned]
            if (not link.up or link.latency_ms > flow.max_latency_ms
                    or link.jitter_ms > flow.max_jitter_ms or link.loss_pct > flow.max_loss_pct):
                del controller.active[flow_id]
                affected.append(flow)
        for flow in affected:
            assigned = controller.admit(flow)
            action = "rerouted" if assigned else "dropped"
            counters[action] += 1
            record(tick, flow, action, assigned)
        for flow in flows:
            if flow.arrival == tick:
                assigned = controller.admit(flow)
                action = "admitted" if assigned else "rejected"
                counters[action] += 1
                record(tick, flow, action, assigned)
        load = {link_name: round(controller.used(link_name), 6) for link_name in controller.links}
        served += sum(controller.used(link_name) for link_name in controller.links)
        snapshots.append(dict(tick=tick, load_mbps=load,
                              active_flows=len(controller.active)))
    requested = sum(f.duration * f.demand_mbps for f in flows)
    return dict(policy=policy, summary={**counters, "requested_mbps_ticks": requested,
                "served_mbps_ticks": round(served, 6),
                "service_ratio": round(served / requested, 6) if requested else 1.0},
                decisions=log, snapshots=snapshots)
