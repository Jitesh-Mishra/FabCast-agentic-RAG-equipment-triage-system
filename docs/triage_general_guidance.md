# Triage — General Guidance

## Reading multiple metrics together
A single metric moving (especially metric2, metric7, or metric9 alone)
is weak evidence — log it, watch it, don't escalate on its own.
Multiple metrics moving together, or metric4 moving at all, is strong
evidence and should be escalated. Corroboration across channels is the
single best confidence booster available in this data; treat it
accordingly.

## Phrasing confidence in a diagnosis
- Don't state failure as certain based on telemetry alone, even when
  metric4 has triggered. Use risk language: "elevated failure risk,"
  "consistent with pre-failure pattern," not "device will fail."
- Don't state a device is safe based on flat telemetry. See
  silent_failure_patterns.md — absence of a signal is not absence of
  risk.
- Be explicit about which metrics drove the assessment and what they
  showed, so a human reviewer can sanity-check the reasoning rather
  than just trusting a score.

## Human sign-off requirement
Every automated flag — regardless of confidence level or which
metric(s) triggered it — requires human review before a work order is
created. The system's job is to surface and rank risk, not to make the
final call. This applies even to metric4-only triggers, which are the
strongest signal available but still produced false positives in
backtesting.

## Quick reference
- metric4 nonzero → urgent, escalate immediately, human confirms.
- Multiple secondary metrics (metric2/7/9) moving together → escalate,
  human confirms.
- Single secondary metric moving alone → log and monitor.
- All flat → no anomaly detected; routine inspection schedule still
  applies.
