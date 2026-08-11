# metric9 — Overview

## Status
Secondary signal, moderate strength.

## Pattern
metric9 follows the same sparse-counter shape as metric2, metric4, and
metric7: normally at 0, with a shift to sustained nonzero values
associated with elevated failure risk in the days beforehand. Its
correlation with failure is moderate — stronger than metric2 or
metric7 individually would suggest as a standalone rule, but not close
to metric4's hit rate.

## Guidance
- A metric9 nonzero reading on its own is worth logging and watching,
  not immediate escalation.
- If metric9 moves together with metric4, treat the device as high
  priority — corroboration across channels increases confidence more
  than any single reading.
- If metric9 is the only channel that has moved, schedule a routine
  check rather than an urgent one, and re-check the next telemetry
  cycle to see if the pattern is sustained or a one-off spike.

## Disposition
Moderate supporting signal. Combine with metric4 and metric2 for
triage decisions rather than acting on it alone.
