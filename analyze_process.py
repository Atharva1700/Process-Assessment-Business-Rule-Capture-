"""Measures the as-is refund process from its event log."""

from pathlib import Path

import pandas as pd

LOG = Path(__file__).parent / "data" / "event_log.csv"


def case_metrics(log):
    """One row per case: cycle time, whether it looped back, and how long the loop took."""
    rows = []
    for case_id, g in log.groupby("case_id"):
        g = g.sort_values("day").set_index("activity")["day"]
        start = g.get("intake")
        end = g.max()
        bounced = "request_receipt" in g.index
        loop_days = (g["intake_resubmit"] - g["request_receipt"]) if bounced else 0.0
        rows.append({
            "case_id": case_id,
            "cycle_days": end - start,
            "bounced": bounced,
            "loop_days": loop_days,
            "expired": "decision_reject_expired" in g.index,
            "manager": "manager_approved" in g.index,
        })
    return pd.DataFrame(rows)


def main():
    log = pd.read_csv(LOG)
    m = case_metrics(log)
    decided = m[~m.expired]

    print(f"cases: {len(m)}   rejected as expired: {m.expired.mean():.1%}")
    print(f"receipt bounce rate: {m.bounced.mean():.1%}")
    print(f"mean cycle time, all cases: {m.cycle_days.mean():.2f} days")
    print(f"mean cycle time, bounced:   {m[m.bounced].cycle_days.mean():.2f} days")
    print(f"mean cycle time, not bounced: {m[~m.bounced].cycle_days.mean():.2f} days")
    print(f"mean loop time (request -> resubmit): {m[m.bounced].loop_days.mean():.2f} days\n")

    # Counterfactual: collect the receipt at intake, so the loop never happens.
    projected = m.cycle_days - m.loop_days
    print(f"projected mean cycle time with receipt at intake: {projected.mean():.2f} days "
          f"(saving {m.cycle_days.mean() - projected.mean():.2f} days per case)")
    print(f"share of cases that would have no loop: {m.bounced.mean():.1%}\n")

    print("manager approval cases:", int(decided.manager.sum()))
    print("auto-approved cases:", int(((~decided.manager)).sum()))


if __name__ == "__main__":
    main()
