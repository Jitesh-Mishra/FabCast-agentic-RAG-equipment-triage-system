# metric2 — Overview

## Status
Monitored, secondary diagnostic signal.

## Normal range
metric2 is a sparse counter. On the large majority of device-days it
reads exactly 0. Brief, isolated non-zero readings occur occasionally
in healthy devices and are not by themselves concerning.

## What a sustained rise indicates
A sustained-nonzero pattern — metric2 staying above 0 across
consecutive days rather than a single spike — is associated with
elevated failure risk. Analysis of confirmed failure cases shows this
channel moving into sustained-nonzero territory ahead of some (not
all) failures.

## Recommended check
If metric2 goes sustained-nonzero:
- Cross-check metric4, metric7, and metric9 for the same device over
  the same window.
- If metric4 has also gone nonzero, prioritize this device — see
  metric4_overview.md.
- If metric2 is the only channel moving, log it and schedule a routine
  visual/physical check rather than an urgent one.

## Disposition
Use as supporting evidence, not a standalone trigger.
