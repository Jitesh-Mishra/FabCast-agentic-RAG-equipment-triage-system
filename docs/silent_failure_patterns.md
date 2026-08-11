# Silent Failure Patterns

## Summary
Not all failures show up in telemetry ahead of time. In the confirmed
failure cases reviewed, roughly one in three showed no detectable
change in any of the nine tracked metrics in the 14 days before
failure. These are genuinely silent failures — the sensors were
reading normally right up until the device went down.

## What this means in practice
- A clean dashboard (all metrics flat, no flags raised) is not
  confirmation that a device is healthy. It means telemetry hasn't
  detected a problem — which is a different, weaker claim.
- Do not tell a requester or a manager that a device is "confirmed
  healthy" based on telemetry alone. The correct phrasing is that
  "no risk indicators are currently present in telemetry."
- Automated flagging (metric4, metric2/7/9 patterns) will continue to
  catch a meaningful share of failures early, but it has a real,
  known ceiling. It is a risk-reduction tool, not a guarantee.

## Operational implication
Periodic physical/visual inspection schedules should not be reduced or
replaced on the assumption that telemetry monitoring covers
everything. Telemetry and physical inspection are complementary, not
substitutes for each other — inspection is the only way to catch the
failures this system structurally cannot see coming.

## Guidance for the triage agent
When telemetry shows no anomaly for a device, avoid absolute language
("no risk", "device is fine"). Use bounded language ("no anomaly
detected in current telemetry; routine inspection still applies per
schedule").
