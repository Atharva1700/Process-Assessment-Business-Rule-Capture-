# Process Assessment and Business Rule Capture: Refund Requests

A simulated refund-request process, assessed from its event log. The results give a
redesigned intake process, and the decision logic is captured in a version-controlled
table that persists after the engagement.

**The process and its event log are simulated.** The receipt rate, the loop delay,
and the 30-day window are parameters of the generator. The analysis measures what the
simulation produced; it does not establish how any real refund process behaves.

## Files

```
process_assessment.md       As-is and future-state diagrams (Mermaid), findings, open questions
simulate_log.py             Generates data/event_log.csv for 1,000 cases
analyze_process.py          Measures cycle time, loop rate, and the counterfactual
data/event_log.csv          The simulated event log
rules/refund_rules.csv      The decision table: the captured business rules
rules/evaluate.py           Applies the table (first match wins, blank bounds mean no limit)
tests/test_rules.py         Example claims per rule, plus a check that every case is covered
```

## Run

```bash
python3 simulate_log.py
python3 analyze_process.py
python3 -m pytest
```

## Why the rules live in a CSV

Decision logic in a spreadsheet or in someone's head is lost when the person leaves.
A CSV in version control is readable by a non-engineer, shows every change in the
diff, and can be checked by tests. Rule changes go through the same review as code.

## Limits

- The loop delay (1-5 days) and the manager wait (0.5-2 days) are assumed, not observed.
- The counterfactual assumes the loop disappears completely. In practice some customers
  will still submit incomplete requests.
- The decision table covers five rules. The real policy is likely to have exceptions
  (for example, product categories with different windows) that were not in the data.
