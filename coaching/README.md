# Sprint coaching layer

Athlete-neutral coaching knowledge and tools for the sprint project. Personal athlete files (the coaching identity, persona and logs) are kept out of this public repository.

| File | What it is |
|---|---|
| `altis-short-sprints.md` | ALTIS *Coaching the Short Sprints*: the course map module by module, with verified evidence, ALTIS's programming model (taken from its free elite 200 m e-book), what a coach is made of, where ALTIS disagrees with other schools, and the Price → Lever → Calendar → Proof decision method. A source ledger at the top says what was read and what was not. |
| `tools/sprintstats.py` | Standard-library sprint statistics: typical error, cue test, stop rule, fly speed, blind scoring, and `race`, a 100 m velocity-curve simulation that ranks levers in race-time. Run `python3 coaching/tools/sprintstats.py selftest` first. |

Every number carries a label: measured, estimated, placeholder or simulation.
