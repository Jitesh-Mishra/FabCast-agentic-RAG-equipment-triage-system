# metric7 — Overview

## Status
Secondary signal, supporting evidence.

## Pattern
metric7 is a sparse, spiky counter similar in shape to metric4 — mostly
0, with failure-associated devices showing a shift to sustained nonzero
values. The correlation with failure is real but weaker and less
consistent than metric4's.

## Guidance
- Treat a metric7 nonzero reading as supporting evidence, not a
  standalone trigger.
- If metric7 moves alongside metric4 (or metric2/metric9), confidence
  in the flag increases significantly — prioritize accordingly.
- If metric7 moves alone with everything else flat, log it and monitor;
  don't escalate to an urgent work order on this signal by itself.

## Note
metric8 tracks statistically identically to metric7 across all analysis
done so far and is very likely a duplicate sensor channel. See
metric8_overview.md. Don't double-count metric7 and metric8 movement as
two independent signals.

## Disposition
Secondary/corroborating channel. Use in combination, not isolation.
