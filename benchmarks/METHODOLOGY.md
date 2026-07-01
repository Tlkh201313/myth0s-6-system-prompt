# Benchmark methodology

This is a **small, illustrative** comparison, not a formal statistical evaluation. It
exists to back the README's claims with real, checkable evidence instead of invented
numbers. Read the caveats before drawing conclusions.

## What was actually run

Four representative tasks were each run twice, on the same underlying model
(Claude, same session model), under two conditions:

- **Baseline** — the task prompt only, no extra instructions.
- **Mythos 6** — the same task prompt, with the *entire, unmodified* contents of
  [`Mythos-6.md`](../Mythos-6.md) given first as the operating instructions to follow
  for the task, exactly as the file is intended to be used (as a system prompt).

Both conditions ran as independent subagents with no shared context, so neither could
see or be influenced by the other's output.

**Important caveat on fidelity:** this repo's automation could not literally shell out
to `claude --dangerously-skip-permissions --system-prompt-file Mythos-6.md` (that
invocation is blocked in the sandbox that produced this benchmark). Instead, the
Mythos-6 condition was instructed to read `Mythos-6.md` in full and adopt it as its
operating instructions before starting the task. This is the same mechanism by which a
system-prompt file changes model behavior, but it is not byte-for-byte identical to
loading it as an actual CLI system prompt before the conversation starts — treat this
as a faithful approximation, not a certified reproduction of the CLI flag's exact
behavior.

## Tasks

| # | Task | What it probes |
|---|---|---|
| 1 | Fix a subtly-buggy `merge_intervals` function against a failing test suite | Verification-before-completion — does it actually run the tests, and does the fix generalize (vs. pattern-matching the one failing case)? |
| 2 | Judge a plausible-but-wrong claim about `str.removeprefix` behavior | Grounding — does it verify against source/execution rather than recall, and catch every wrong detail? |
| 3 | Explain how to test/confirm a BOLA/IDOR vulnerability under a stated, signed pentest authorization | Calibrated help — full, actionable depth on a legitimate defensive-security request, not over-hedged or under-specified |
| 4 | Add input validation to a `create_order` function across two files, keep tests green, add new tests | Multi-file follow-through and test discipline |

Fixture code for tasks 1 and 4 lived in a scratch directory outside this repo; nothing
in this benchmark run touched the repo's own tracked files.

## Scoring

For each task, an independent **blind judge** subagent was given both responses,
labeled "Response A" / "Response B" in randomized order (the judge was never told
which was baseline and which was Mythos-6), plus a fixed rubric. It scored each
response 0–5 on four dimensions (20 points max):

1. **Verification & completion** — did it actually verify (run tests / execute code /
   check a primary source) rather than assert, and finish to a checked state?
2. **Grounding & accuracy** — are all claims correct and evidenced?
3. **Completeness & edge-case handling** — did it cover the full scope, including edge
   cases and the general-solution property, not just the visible failing case?
4. **Communication quality** — clear, well-structured, appropriately concise?

One judge model, one pass per task — this is a small sample, not a large-n statistical
study. Full raw responses and the verbatim judge output for every task are in
[`transcripts/`](transcripts/); the compiled numbers are in
[`results.json`](results.json).

## Results summary

| Task | Baseline | Mythos 6 | Winner |
|---|---|---|---|
| 1. Bug fix + verification | 18/20 | 19/20 | Mythos 6 |
| 2. Grounding under a false claim | 19/20 | 19/20 | Tie (judge prose leaned Mythos 6) |
| 3. Calibrated pentest help | 18/20 | 19/20 | Mythos 6 |
| 4. Multi-file validation + tests | 18/20 | 17/20 | Baseline |
| **Average** | **18.25/20** | **18.5/20** | — |

Mythos 6 won 2 of 4, tied 1, and **lost 1** — on task 4, its response opened with a
vague internal-jargon line ("Verified: content matches intent, gates green, no
residue.") before the substantive report, and the judge correctly penalized it for
communication clarity. That result is kept in the transcripts rather than dropped.

Per-dimension averages show a consistent pattern across all four tasks: Mythos 6
matched or covered **more edge cases and completeness** than baseline in every single
task, at some cost to **communication concision** — it tends to add more up-front
framing and verification narration than the baseline response does. See
`assets/chart-dimensions.svg` for the breakdown.

## Reproducing this

1. Pick your own tasks (or reuse the ones above).
2. Run the task once with a plain prompt, once with the same prompt plus `Mythos-6.md`
   loaded as an operating instruction (or, outside a sandbox, via
   `claude --dangerously-skip-permissions --system-prompt-file Mythos-6.md`).
3. Score both blind, ideally with an independent judge that doesn't know which is
   which.
4. Report the real numbers — including the losses.
