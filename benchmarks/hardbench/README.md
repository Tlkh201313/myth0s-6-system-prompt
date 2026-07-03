# hardbench — a hard, deterministic reasoning benchmark for Mythos 6

This is a second, much harder benchmark than the 4-task LLM-judge study in
[`../METHODOLOGY.md`](../METHODOLOGY.md). It was built to answer a blunt question:

> *Take the hardest questions an AI fails, and improve the prompt until it can answer them.*

The honest result is more interesting than that framing assumes. **On a strong 2025 model,
there is almost no reasoning-accuracy headroom left for a system prompt to recover — the model
already answers hard reasoning cold. The one place the prompt makes a large, reliable, measurable
difference is *tool discipline* on the model's genuine blind spots (character counting, big-integer
arithmetic, date math), where it lifts a plain assistant from 73% to 100%.**

Everything here is deterministically graded (no LLM judge), every logic puzzle is verified by a
brute-force solver to have a unique solution, and every number is real. No result was tuned or
invented.

## TL;DR results

| Battery | What it tests | Condition | Pass rate |
|---|---|---|---|
| v1 classic-trap (64 Q) | famous riddles, altered constants | naked reasoning | **62/64 (97%)** |
| v2 hard-reasoning (36 Q) | knights & knaves, zebra grids, exact combinatorics, multi-step traps | naked reasoning | **35.7/36 (99%)** |
| v3 edge (16 Q) | 5-house Einstein puzzles, 4-speaker K&K, 12-step trap problems, long-string counting | naked reasoning | **14.3/16 (89%)** |
| v4 tool-fixable (11 Q) | long-string counting, big-int arithmetic, date deltas | **BASE** (plain assistant, tools on) | **8.0/11 (73%)** |
| v4 tool-fixable (11 Q) | " | **MYTHOS** (operating under `Mythos-6.md`, tools on) | **11/11 (100%)** |

Test model: `claude-haiku-4-5` (the weaker, faster model — where any headroom would show; a
frontier model is even more saturated). k = 3 runs per condition. Battery hashes and the frozen
pre-registration are in [`PREREGISTRATION.txt`](PREREGISTRATION.txt);
machine-readable numbers in [`RESULTS_SUMMARY.json`](RESULTS_SUMMARY.json).

## The three findings

1. **Reasoning is at ceiling.** From pure reasoning (no tools), the naked model solved essentially
   every solvable puzzle we could author — including a full 5-house Einstein/zebra puzzle, 4-speaker
   knights-and-knaves, exact probability as reduced fractions, and 12-step trap word problems. Across
   v1–v3 (116 questions) the *only* robust failures were long-string **character counting** (e.g.
   miscounting the letter `e` in a 140-character sentence, 31→32). You cannot "improve the prompt
   until it answers these" by sharpening reasoning rules — the model already answers them.

2. **The one real failure mode is tool-fixable, not reasoning-fixable.** Character counting and
   large-integer arithmetic are *tokenizer / mental-math* limits: no amount of "think carefully"
   fixes them reliably, but a one-line tool call does. This is precisely what Mythos 6's
   `reasoning_and_evidence` rule already mandates ("use tools for multi-digit arithmetic, date deltas,
   conversions, statistics, counting").

3. **Mythos 6 already captures that gain — reliably.** On the tool-fixable battery with tools
   available to both conditions, a plain assistant used tools only *sometimes* (73%, and highly
   variable run-to-run: 11, 7, 6 out of 11). Operating under Mythos 6, the model used tools **every
   time** and scored **11/11 on all three runs** — 6 questions fixed, **zero regressions**. Subagent
   tool-call counts confirm the mechanism: BASE runs used 2–3 tool calls (mostly just read/write and
   answered from memory); MYTHOS runs used 4–9 (they actually computed).

### Why no prompt edit was made
The plan behind this benchmark said: *ship a prompt change only if it lifts a failing case with no
regression.* Mythos 6 already scores **100%** on the only battery with any headroom, so there was
nothing to lift — and inventing an edit to claim an improvement would be dishonest. The rigorous
outcome is a **validation** of the existing prompt, plus a clear ceiling result: remaining failures
(genuine frontier problems) are capability limits no system prompt can move.

## Method

- **Conditions** (fresh, isolated subagents per run): **BASE** = task only; **MYTHOS** = the full
  unmodified `Mythos-6.md` adopted as operating instructions, then the task; (a generic-effort
  control is described in the plan but the ceiling result made it moot for v1–v3).
- **Tools:** v1–v3 were run *tools-off* (to isolate pure reasoning). v4 was run *tools-on* (to test
  tool discipline — the prompt's actual mechanism).
- **Grading:** 100% deterministic — exact numeric / string / structured match, code executed against
  hidden boundary tests, logic puzzles checked against solver-computed keys. No LLM judge decides
  pass/fail. The grader self-tests to 64/64 and 36/36 on gold answer sheets before any run is trusted.
- **Question integrity:** every logic puzzle is generated or verified by a brute-force solver that
  asserts a *unique* solution; classic riddles use *altered constants* so a memorized answer is wrong.

## Honest caveats
- Small n (11–64 per battery, k=3), single model, single date. This supports *relative* before/after
  comparison, not a precise effect size.
- **Fidelity:** as with the original study, the sandbox cannot shell out to a real
  `--system-prompt-file`; the MYTHOS condition reads and adopts the file. That is how a system prompt
  changes behavior, but it is not byte-identical to the CLI flag. Temperature/seed are not
  controllable here.
- Runs are batched (one subagent answers a whole battery), not one-isolated-context-per-question.
- The v3 5-house zebra generator is brute-force and slow to *build* (~40 min); the questions
  themselves are cheap to answer.

## Reproduce
```
cd benchmarks/hardbench
python3 build.py && python3 build2.py && python3 build4.py   # regenerate batteries (+ build3.py, slow)
python3 grade.py runs/<answers>.txt --q=questions2.json      # grade any answer sheet
```
Raw model answer sheets for every run are in [`runs/`](runs/).
