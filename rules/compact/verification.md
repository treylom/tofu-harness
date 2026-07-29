# Rule: verification before completion (compact)

Trigger: about to say "done", "fixed", "verified", "passing" — or ending a turn after changing code/config.

1. **Evidence before claims.** Before claiming, run the narrowest command that would fail if you're wrong (a test, `bash -n`, a diff, a re-read) and read its output. No fresh evidence = it's a guess.
2. **State the verification grade.** ① script/assert ② end-to-end replay ③ independent evaluator ④ human review — name the rung that actually ran. Don't let ① stand in for ③.
3. **3-tier inputs when it matters.** ① happy path ② deep (bigger windows, all switches) ③ boundary (empty, off-by-one, skip paths). If only ① was needed, say so.
4. **Name the layer you verified at.** source → build → render → consumer. A middle-layer pass does not transfer up; claim the layer you actually checked, or downgrade ("verified at build layer only").
5. **Absence claims need boundary expansion first.** Before "X doesn't exist / no other Y / that's everything":
   - if the claim concerns a repo/codebase: `git log --oneline --all` and `git branch -a` — unmerged branches hold "missing" things
   - re-run the search unfiltered and untruncated (no head/limit), with synonym vocabulary
   - isolate the input so only X can match (a clean probe beats one broad grep)
   - then claim absence citing the boundary you checked, or downgrade ("not in the checked-out tree").
6. **Verify a "broken" premise before building around it.** Walk cache-staleness → async lag → intermediary layer, measure in YOUR runtime, read the official docs — then decide.
7. **Re-measure volatile state after a context reset.** Post-compaction/handoff memory of connections, quotas, tool health is stale; probe before declaring "unavailable".
8. **Spend review where errors originate.** Review the spec/outline before the artifact — that's the cheapest verification available.
9. **Verify the verifier.** If a success message and your own check disagree, build a third, stricter measurement (parse structure, don't substring-match); suspect the checker too.
10. **Attribute before learning from a failure.** In mixed-model/multi-worker sessions, pin the failure to its producer via per-turn metadata, not narrative.
11. **Diff every quote against its source mechanically** (normalize whitespace/quote-style/ellipses) before publishing; re-check every copy of a repeated quote, not one.
12. **A sample is not a batch.** Multi-item deliverable = per-item pass/fail sweep of the stage you just ran, not item 1 + optimism.
13. **Read the gate's definition before prescribing on its FAIL** (non-obvious failures): open the gate's code/docstring once, prescribe, then re-measure with the same gate (FAIL→PASS).
14. **Verifiers carry the same evidence bar**: measure the consumer-visible surface before declaring RED, not static source alone; keep source defects (warn) apart from delivery defects (hard).
15. **Prescriptions get their own threats line; runnable prescriptions get run first.** Add "what new loss does this create"; before structural changes compare against existing mechanisms once; self-check with "what observation can't this explain?" instead of "maybe I overdid it".
