"""Tests for the refund decision table. The table is the spec: each case here reflects
a business rule as a person would state it, not as the code computes it.
"""

import itertools
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rules.evaluate import decide, load_rules  # noqa: E402


@pytest.mark.parametrize("amount, has_receipt, age_days, expected, rule", [
    (0, True, 5, "reject_invalid", "R01"),          # zero amount
    (-20, False, 5, "reject_invalid", "R01"),       # negative amount beats missing receipt
    (50, False, 5, "request_receipt", "R02"),       # no receipt
    (50, True, 45, "reject_expired", "R03"),        # 45 days old
    (50, True, 30, "auto_approve", "R04"),          # exactly 30 days is inside the window
    (100, True, 10, "auto_approve", "R04"),         # exactly 100 is not over 100
    (100.01, True, 10, "manager_approval", "R05"),  # just over 100
    (250, True, 1, "manager_approval", "R05"),
])
def test_example_claims(amount, has_receipt, age_days, expected, rule):
    claim = {"amount": amount, "has_receipt": has_receipt, "age_days": age_days}
    assert decide(claim) == (expected, rule)


def test_rule_priorities_are_unique_and_loaded_in_order():
    rules = load_rules()
    assert [r["priority"] for r in rules] == sorted(r["priority"] for r in rules)
    assert len({r["rule_id"] for r in rules}) == len(rules)


def test_every_combination_is_covered_by_some_rule():
    """No claim should fall through the table. A gap here is a missing business rule."""
    amounts = [-5, 0, 0.01, 50, 100, 100.01, 500]
    ages = [0, 30, 31, 90]
    for amount, receipt, age in itertools.product(amounts, [True, False], ages):
        decision, _ = decide({"amount": amount, "has_receipt": receipt, "age_days": age})
        assert decision in {"reject_invalid", "request_receipt", "reject_expired",
                            "auto_approve", "manager_approval"}
