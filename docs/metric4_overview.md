# metric4 — Overview

## Status
Primary automated trigger. Strongest single signal in the telemetry set.

## Pattern
metric4 is a sparse counter that sits at exactly 0 for weeks at a time
under normal operation. In confirmed failure cases, it transitions from
0 to a sustained nonzero value 1-2 days before failure. This 0-to-nonzero
transition is the single most reliable early warning available in this
telemetry set.

## Performance
A simple rule — flag the device if metric4 > 0 — caught 13 of 23
held-out confirmed failures on its own, with no other logic involved.
No other single metric comes close to this hit rate.

## Guidance
- Any device where metric4 moves from 0 to nonzero should be flagged
  immediately for review, regardless of what other metrics are doing.
- Because the transition typically precedes failure by only 1-2 days,
  treat this as urgent, not routine.
- metric4 > 0 does not guarantee failure is imminent — it is a strong
  risk signal, not a certainty. Confirm with a physical check before
  taking the device offline.

## Limits
metric4 does not catch everything. Roughly a third of confirmed
failures show no change in this or any other metric beforehand — see
silent_failure_patterns.md. A quiet metric4 is not a clearance.

## Disposition
Primary trigger. Weight this channel heaviest in any automated scoring.
