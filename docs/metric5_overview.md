# metric5 — Overview

## Status
Low diagnostic value.

## Description
Like metric3, metric5 shows no meaningful separation between failing
and healthy devices in the analysis to date. It behaves as a
slow-moving cumulative counter, more reflective of device age or
configuration history than of current operating condition.

## Guidance
Don't weight metric5 in failure-risk scoring or use it as a trigger
for inspection. It can be useful context when reviewing a device's
overall history (e.g., comparing units of similar vintage), but it
adds no acute-risk information.

## Disposition
Keep for reference/lifecycle context. Exclude from diagnostic scoring.
