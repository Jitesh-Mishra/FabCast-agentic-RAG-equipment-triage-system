# metric1 — Overview

## Status
Monitored, low diagnostic value.

## Description
metric1 is collected daily across all devices as part of the standard
telemetry set. Historical analysis (device-day records, matched against
confirmed failure events) found no meaningful separation between failing
and healthy devices on this channel. Values are noisy and high-variance
regardless of device health state.

## Why it's not useful for triage
Across the dataset, metric1's distribution in the 14 days before a
confirmed failure is statistically indistinguishable from its
distribution during normal operation. No threshold or trend rule on
metric1 alone produced better-than-chance separation in backtesting.

## Guidance
Do not use metric1 as a standalone trigger for inspection or a work
order. It can still be logged and displayed for completeness, but it
should not carry weight in an automated flag or a manual diagnosis. If
metric1 shows an unusual reading, treat it as noise unless it co-occurs
with a move in metric2, metric4, metric7, or metric9.

## Disposition
Keep collecting (cheap, no reason to drop), but exclude from
diagnostic scoring logic.
