# metric8 — Overview

## Status
Likely duplicate of metric7. Deprioritize in triage.

## Description
metric8 is statistically identical to metric7 across every analysis
run so far — same distribution, same behavior relative to failing vs.
healthy devices. This strongly suggests metric8 is a duplicate or
redundant sensor channel rather than an independent measurement.

## Guidance
- Do not treat metric7 and metric8 moving together as two independent
  confirming signals — they're very likely the same underlying signal
  reported twice.
- If metric8 is the only channel showing movement and metric7 is flat,
  that's unusual given how closely they track and is worth a second
  look at the sensor/data pipeline itself before treating it as a
  genuine health signal.
- For scoring purposes, use metric7 as the representative channel and
  treat metric8 as redundant.

## Disposition
Deprioritize. Flag for the data/sensor team as a candidate for
consolidation or retirement.
