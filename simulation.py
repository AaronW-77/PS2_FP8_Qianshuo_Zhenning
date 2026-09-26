"""FP8 PS2: paired, one-shot allocation experiment (Python standard library)."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import random
import statistics as st
from dataclasses import asdict, dataclass
from pathlib import Path

SEED = 20260926
BATCHES = 1000


@dataclass(frozen=True)
class Request:
    pm: int
    value: float
    exposure: float
    severity: float
    arrival: int
    shading: float = 0.8
    budget: float = 100.0

    @property
    def risk(self):
        return 100 * self.exposure * self.severity

    @property
    def bid(self):
        return min(self.budget, self.shading * self.value)


def generate_batches(seed=SEED, count=BATCHES, alignment="independent", heterogeneous=False):
    """Same draws across scenarios. Sorted/reversed values are alignment stress tests."""
    rng = random.Random(seed)
    for _ in range(count):
        values = [100 * rng.random() for _ in range(20)]
        exposures = [rng.random() for _ in range(20)]
        severities = [rng.random() for _ in range(20)]
        arrival = list(range(20))
        rng.shuffle(arrival)
        shade = [0.5 + 0.5 * rng.random() for _ in range(20)]
        if alignment != "independent":
            rank = sorted(range(20), key=lambda j: (exposures[j] * severities[j], j))
            assigned = sorted(values, reverse=(alignment == "opposed"))
            values = dict(zip(rank, assigned))
        yield [Request(j + 1, values[j], exposures[j], severities[j], arrival[j],
                       shade[j] if heterogeneous else 0.8) for j in range(20)]


def allocate(requests, mechanism, slots=4, reserve=1, threshold=60):
    """Return {PM: payment}. Lower PM ID breaks all exact score/bid/arrival ties."""
    if mechanism not in ("pure", "hybrid", "fcfs"):
        raise ValueError("unknown mechanism")
    if not 0 <= reserve <= slots or slots < 0:
        raise ValueError("invalid reserve/slots")
    if len({r.pm for r in requests}) != len(requests):
        raise ValueError("duplicate PM")
    if any(not (0 <= r.value <= 100 and 0 <= r.exposure <= 1 and
                0 <= r.severity <= 1 and 0 <= r.shading <= 1 and r.budget >= 0)
           for r in requests):
        raise ValueError("invalid request")
    winners = {}
    if mechanism == "fcfs":
        return {r.pm: 0.0 for r in sorted(requests, key=lambda r: (r.arrival, r.pm))[:slots]}
    if mechanism == "hybrid":
        eligible = sorted((r for r in requests if r.risk >= threshold),
                          key=lambda r: (-r.risk, r.pm))
        winners = {r.pm: 0.0 for r in eligible[:reserve]}
    remaining = sorted((r for r in requests if r.pm not in winners),
                       key=lambda r: (-r.bid, r.pm))
    winners.update({r.pm: r.bid for r in remaining[:slots-len(winners)]})
    return winners


def metrics(requests, allocation, threshold=60, weight=1.0):
    chosen = [r for r in requests if r.pm in allocation]
    value = sum(r.value for r in chosen)
    risk = sum(r.risk for r in chosen)
    payment = sum(allocation.values())
    optimum = sum(sorted((r.value for r in requests), reverse=True)[:4])
    eligible = sum(r.risk >= threshold for r in requests)
    return dict(V=value, C=risk, W=value + weight*risk, payment=payment,
                utility=value-payment, efficiency=value/optimum if optimum else None,
                eligible_access=(sum(r.risk >= threshold for r in chosen)/eligible
                                 if eligible else None))


def write_csv(path, rows):
    rows = list(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def mean(values):
    values = [v for v in values if v is not None]
    return st.mean(values) if values else None


def run(out="results", seed=SEED, count=BATCHES):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    batches = list(generate_batches(seed, count))
    records, individuals = [], []
    demo = batches[0]
    write_csv(out/"demo_inputs.csv", [dict(**asdict(r), risk=r.risk, bid=r.bid) for r in demo])
    for batch, requests in enumerate(batches, 1):
        for mechanism in ("pure", "hybrid", "fcfs"):
            allocation = allocate(requests, mechanism)
            records.append(dict(batch=batch, mechanism=mechanism,
                                winners=";".join(map(str, sorted(allocation))),
                                **metrics(requests, allocation)))
            if batch == 1:
                for r in requests:
                    p = allocation.get(r.pm, 0)
                    x = int(r.pm in allocation)
                    individuals.append(dict(mechanism=mechanism, pm=r.pm, value=r.value,
                                            risk=r.risk, bid=r.bid, allocated=x, payment=p,
                                            utility=x*r.value-p, credits_left=r.budget-p))
    write_csv(out/"demo_allocations.csv", individuals)
    write_csv(out/"primary_batches.csv", records)
    summary = []
    for mechanism in ("pure", "hybrid", "fcfs"):
        subset = [r for r in records if r["mechanism"] == mechanism]
        summary.append(dict(mechanism=mechanism, batches=count,
                            **{k: mean(r[k] for r in subset)
                               for k in ("V", "C", "W", "payment", "utility", "efficiency", "eligible_access")}))
    write_csv(out/"primary_summary.csv", summary)
    sensitivity = []
    for alignment in ("independent", "aligned", "opposed"):
        for hetero in (False, True):
            sample = list(generate_batches(seed, count, alignment, hetero))
            for threshold in (40, 60, 80):
                for reserve in (1, 2):
                    pairs = []
                    for requests in sample:
                        p = metrics(requests, allocate(requests, "pure"), threshold)
                        h = metrics(requests, allocate(requests, "hybrid", reserve=reserve,
                                                       threshold=threshold), threshold)
                        pairs.append((h["V"]-p["V"], h["C"]-p["C"]))
                    dv, dc = mean(p[0] for p in pairs), mean(p[1] for p in pairs)
                    dw = [v+c for v,c in pairs]
                    se = st.stdev(dw)/(count**0.5) if count > 1 else 0
                    sensitivity.append(dict(alignment=alignment, bid_rule="heterogeneous" if hetero else "0.8v",
                                            threshold=threshold, reserve=reserve, delta_V=dv, delta_C=dc,
                                            delta_W_lambda0=dv, delta_W_lambda05=dv+0.5*dc,
                                            delta_W_lambda1=dv+dc, delta_W_lambda2=dv+2*dc,
                                            MC_SE_lambda1=se, fraction_strictly_better=mean(x>1e-10 for x in dw),
                                            mean_break_even_lambda=(-dv/dc if dc>1e-10 else None)))
    write_csv(out/"sensitivity.csv", sensitivity)
    source = Path(__file__)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob("*.csv"))}
    manifest = dict(seed=seed, batches=count, python=platform.python_version(), N=20, K=4,
                    credits=100, threshold=60, reserve=1, welfare_weight=1,
                    primary_bid="0.8*v", risk="100*exposure*severity",
                    distributions="independent U[0,100] value; U[0,1] exposure and severity; random arrival",
                    simulation_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), outputs_sha256=hashes)
    (out/"fresh_run.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps(summary, indent=2))
    print("Primary paired comparison:")
    print(json.dumps(next(s for s in sensitivity if s["alignment"] == "independent" and
                         s["bid_rule"] == "0.8v" and s["threshold"] == 60 and s["reserve"] == 1), indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="results")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--batches", type=int, default=BATCHES)
    args = parser.parse_args()
    if args.batches < 1:
        parser.error("batches must be positive")
    run(args.out, args.seed, args.batches)
