"""Applies the refund decision table in refund_rules.csv. Rules are checked in priority
order and the first match wins. Blank bounds mean no limit.

Usage:
  from rules.evaluate import decide
  decide({"amount": 120.0, "has_receipt": True, "age_days": 10})
    -> ("manager_approval", "R05")
"""

import csv
from pathlib import Path

RULES_FILE = Path(__file__).with_name("refund_rules.csv")


def _bound(text):
    return None if text == "" else float(text)


def load_rules(path=RULES_FILE):
    with open(path, newline="") as f:
        rules = [
            {
                "rule_id": r["rule_id"],
                "priority": int(r["priority"]),
                "amount_min": _bound(r["amount_min_exclusive"]),
                "amount_max": _bound(r["amount_max_inclusive"]),
                "receipt": r["receipt"],
                "age_min": _bound(r["age_min_exclusive"]),
                "age_max": _bound(r["age_max_inclusive"]),
                "decision": r["decision"],
            }
            for r in csv.DictReader(f)
        ]
    priorities = [r["priority"] for r in rules]
    if len(set(priorities)) != len(priorities):
        raise ValueError("duplicate priorities in refund_rules.csv")
    return sorted(rules, key=lambda r: r["priority"])


def _in_range(value, low_exclusive, high_inclusive):
    if low_exclusive is not None and not value > low_exclusive:
        return False
    if high_inclusive is not None and not value <= high_inclusive:
        return False
    return True


def _matches(rule, claim):
    if rule["receipt"] == "yes" and not claim["has_receipt"]:
        return False
    if rule["receipt"] == "no" and claim["has_receipt"]:
        return False
    return (_in_range(claim["amount"], rule["amount_min"], rule["amount_max"])
            and _in_range(claim["age_days"], rule["age_min"], rule["age_max"]))


def decide(claim, rules=None):
    for rule in rules or load_rules():
        if _matches(rule, claim):
            return rule["decision"], rule["rule_id"]
    raise LookupError(f"no refund rule matched: {claim}")
