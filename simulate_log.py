"""Simulates an event log for a refund-request process. The process is SIMULATED.

As-is process:
  intake -> receipt check -> eligibility (30-day window) -> approval -> payment -> close

  - Intake does not require a receipt upload, so about 28% of requests have none.
  - A receipt check on a missing receipt sends the request back to the customer (request_receipt),
    who resubmits after 1-5 days, which is a rework loop.
  - Amounts over 100 need manager approval, which waits 0.5-2 days.

Output: data/event_log.csv with one row per (case, activity, day).
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 7
N_CASES = 1000
RECEIPT_RATE = 0.72
OUT = Path(__file__).parent / "data" / "event_log.csv"


def simulate(seed=SEED, n=N_CASES):
    rng = np.random.default_rng(seed)
    rows = []
    for case in range(n):
        case_id = f"R{case:04d}"
        amount = round(float(rng.lognormal(mean=4.0, sigma=0.8)), 2)
        age_days = int(rng.integers(0, 61))
        has_receipt = bool(rng.random() < RECEIPT_RATE)

        t = float(rng.uniform(0, 300))
        rows.append((case_id, "intake", t))
        if not has_receipt:
            rows.append((case_id, "receipt_check_failed", t + 0.1))
            rows.append((case_id, "request_receipt", t + 0.1))
            t = t + 0.1 + float(rng.uniform(1, 5))  # customer resubmits later
            rows.append((case_id, "intake_resubmit", t))
        rows.append((case_id, "receipt_check_passed", t + 0.1))

        if age_days > 30:
            rows.append((case_id, "decision_reject_expired", t + 0.2))
            continue

        t += 0.2
        if amount > 100:
            rows.append((case_id, "manager_approval_requested", t))
            t += float(rng.uniform(0.5, 2))
            rows.append((case_id, "manager_approved", t))
        else:
            rows.append((case_id, "auto_approved", t))
        t += 0.5
        rows.append((case_id, "payment_issued", t))
        rows.append((case_id, "closed", t))

    return pd.DataFrame(rows, columns=["case_id", "activity", "day"])


if __name__ == "__main__":
    OUT.parent.mkdir(exist_ok=True)
    simulate().round(3).to_csv(OUT, index=False)
    print(f"wrote {OUT}")
