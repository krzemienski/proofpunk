# Exact mtime equality under the tie, at nanosecond precision

An earlier probe printed 'tied: False'. That probe measured 80 run-*
directories restored by 'git archive', not the two runs under test —
the alpha/beta pair was tied with each other and differed from the
restored ones. step-13 re-ran it in an isolated tree and printed
'tied: True', but compared floats, and float equality at display
precision is not the same as identical timestamps.

This settles it with st_mtime_ns, which is an integer and admits no
display rounding.

## Subject
  helper from: git archive HEAD (4ab9d1a)
  isolated tree: exactly two run-* directories exist

## Nanosecond timestamps
  run-* directories found: 2
    e2e-evidence/run-20260912T181518-alpha
      st_mtime_ns = 1789236919126786000
    e2e-evidence/run-20260912T181518-beta
      st_mtime_ns = 1789236919126786000

  distinct st_mtime_ns values: 1
  EXACTLY TIED: True

  Which run does a bare (untargeted) call resolve to?
  max() over an exact tie returns whichever the glob order yields —
  that is the ambiguity --run exists to remove.

## Both runs validated by explicit target, under that exact tie
  validate --run <alpha>  unpiped rc=0
    alpha holds one 1200-byte artifact (above the >1024 floor)
    stdout: validate OK: e2e-evidence/run-20260912T181518-alpha
  validate --run <beta>   unpiped rc=2
    beta holds one 50-byte artifact (below the floor)
    stderr: THIN: e2e-evidence/run-20260912T181518-beta/step-01-thin.log (50 bytes, needs > 1024) — too small to carry a claim; re-capture with its command, rc, and surrounding state (evidence-contract.md rule 3)

Two different verdicts from two directories with byte-identical
mtimes. Without --run both calls resolve to one arbitrary winner and
one of these verdicts would be silently wrong — which is exactly the
failure that made my own three-run verification loop report rc=0 for
a run that fails rc=2.
