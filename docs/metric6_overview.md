# metric6 — Overview

## Status
Low diagnostic value.

## Description
metric6 shows the same pattern as metric3 and metric5: little to no
separation between failing and healthy devices, and behavior
consistent with a cumulative counter tied to device age or
configuration rather than current health.

## Guidance
Not useful as a standalone or supporting signal for failure risk. Fine
to keep in the record for lifecycle comparisons across the fleet, but
it shouldn't influence an automated flag or a triage decision.

## Disposition
Keep for reference. Exclude from diagnostic scoring.
