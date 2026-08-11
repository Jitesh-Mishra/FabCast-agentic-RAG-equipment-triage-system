# metric3 — Overview

## Status
Low diagnostic value.

## Description
metric3 readings are nearly identical between devices that
subsequently failed and devices that didn't. Where it does move, it
tends to behave as a slow-moving cumulative counter that tracks
something closer to device age or usage total than acute health
status.

## Guidance
Do not use metric3 as a failure-risk signal. It's fine to reference
when assessing general device wear/lifecycle (e.g., "this unit has
accumulated more X than a comparable one"), but it should not
contribute to an automated risk score or drive an urgent work order.

## Disposition
Keep collecting for lifecycle/age tracking purposes. Exclude from
acute-failure triage logic.
