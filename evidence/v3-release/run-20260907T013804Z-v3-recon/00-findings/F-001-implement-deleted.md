# F-001 — implement/SKILL.md deleted in working tree (unattributed)

Observed: 2026-09-07T01:41:18Z
HEAD: 93c479de800fff7e3ceb0be5ccf96f4d494fdaee

## Evidence

- git status: ` D plugins/proofpunk/skills/implement/SKILL.md`
- HEAD blob sha256: 5ed7370e501388b8d29003fa50bcbba58be4a1c2d893138d8c5890c7250a3e40 (245 lines)
- skills dirs on disk: 17; at HEAD: 18
- router head STILL routes to implement (working-tree diff adds only a run-trace-schema row)
- verify-router-links.py rc=1: "orphan route(s) ... ['implement']"
- verify-orchestration.py rc=1
- verify-counts.py rc=1: 18 doc sites claim "18 skills", live accepts [16,17]
- gauge-report.py #6 UNMET: skill count 17
- HEAD commit body: "17 links DERIVED as N-1 from a glob" => N=18 is intended

## Classification

DEFECT, not intent. Restoring from HEAD destroys nothing (file absent on disk).
