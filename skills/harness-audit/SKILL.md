---
name: harness-audit
description: Use when auditing an AI-agent harness (CLAUDE.md / AGENTS.md / SKILL.md / rules files) for drift — dead links, stale model names, tool mismatches, and cross-document conflicts — then repairing only independently verified findings. Deadline-bounded, parallel-census based, with built-in guards against audit overrun. Especially useful right after a new model release, when official prompting guidance changes underneath your harness.
---

# /harness-audit — census, verify, repair your harness documents

> Origin: a real overnight audit (2026-07-25; a single run, one harness, 252 documents) — full census → 52 suspected defects → independent re-verification → 49 confirmed → all repaired (one commit spanning 47 files + 2 sibling fixes). These aggregates carry their scope label deliberately — per-document verdicts are the reliable unit (STEP 2). The **seven guards below were reverse-engineered from that night's inefficiencies** (over-verification, purpose drift, no deadline), so that running this skill never costs what the first run did.

## When to run this

- **A new model just shipped.** Model vendors now publish model-specific prompting guidance (e.g. Anthropic's *Prompting Claude Opus 5*, released with the model — see the dated source in this repo's README). Every release quietly invalidates some of your harness: model names pinned in docs, thresholds benchmarked on the old generation, instructions the new model no longer needs — or newly needs. This skill is the systematic "does my harness still tell the truth?" pass.
- **Quarterly maintenance**, or whenever a doc's claim visibly disagrees with reality.
- **Before publishing/porting your harness** anywhere else.

## Fixed deliverables (declared at start — guard ②)

Exactly three outputs. Declare them up front; wanting to produce anything else mid-run is your drift alarm.

1. **Census table** — every document × 4 axes, verdict `OK / FINDING / UNREADABLE`
2. **Repair commit(s)** — CONFIRMED findings only, applied centrally
3. **Disposition list** — one line each for what a text edit can't fix (structural calls, files you don't own, deferred judgment)

## The seven guards

| # | Guard | Rule |
|---|---|---|
| ① | **Deadline required** | Ask for an end time before starting (refuse to start open-ended). Reaching it = report what exists. Extensions are the user's call, not yours |
| ② | **Deliverable frame is fixed** | The three outputs above, nothing else — "while I'm at it" is how audits eat the night |
| ③ | **Verification rounds capped at 2** | Re-verifying or re-wording the same target more than twice = escalate to the user instead |
| ④ | **Label fixes only when behavior changes** | Wording/label defects in files you don't own: intervene only if an agent would *act* differently; otherwise record and move on |
| ⑤ | **Parallel by default, workers judge-only** | 30+ documents = parallel worker census (not sequential reading). Workers never edit anything |
| ⑥ | **Measure capacity before fan-out** | Check the machine's concurrent capacity (panes/process headroom) before spawning workers; verify leftover cleanup after |
| ⑦ | **Runtime checks are opt-in** | Document truthfulness is the default scope. *Executing* skills to verify them is a separate, costlier stage — offer it as an upgrade question and run it only if the user says yes |

## Procedure

### STEP 0 — Deadline & frame (guards ①②)
Ask for: the deadline, and the target scope (default: project + user-home `CLAUDE.md` / `AGENTS.md` / `SKILL.md` / rules files). Declare the three deliverables.

### STEP 1 — Fix the denominator first
Build an **independent file list** with `find` *before* scanning — never count while scanning (if existence becomes the entry condition, absences silently fall out of the denominator). Save the list as a JSON array.

### STEP 2 — Four-axis census (guards ⑤⑥)
Parallel workers (~12 docs each) judge every document on four axes:

- **tool-mismatch** — do the tools/paths/servers the doc references exist in the current environment?
- **stale** — are model names, versions, dates, and retired-tool references current?
- **dead-link** — do relative references (`reference/`, `scripts/`, `examples/`) resolve?
- **conflict-dup** — does it contradict another loaded document?

Worker schema: `{path, verdict: OK|FINDING|UNREADABLE, axis, finding}`. **No minimizers in the prompt** ("only report serious ones" shrinks output literally) — collect everything, filter downstream.
**Include a unit-definition example in the worker prompt.** Without "here is what counts as one finding", extraction criteria diverge per worker and aggregate counts don't reproduce (measured: verdict agreement 86–88%, extraction agreement 26–41%). Trust per-document verdicts; never quote aggregate counts standalone.

### STEP 3 — Independent re-verification + fix proposals (two-stage)
Feed FINDINGs to **different workers who re-verify from scratch**: `{verdict: CONFIRMED|REFUTED|UNCERTAIN, evidence (one measured line), fix_type: edit|policy|none, old_string?, new_string?}`. Workers stay read-only; `old_string` must be verbatim and uniquely matchable. **Don't punish UNCERTAIN** — a wrong fix is worse than no fix. (In the origin run this stage overturned 3 of 52 first-pass findings.)

### STEP 4 — Central batch apply
Apply CONFIRMED+edit through one applier (replace only when the match count is exactly 1; report failures) → stage files by name → commit. `policy` items go to the disposition list (banners, retirement notices, owner notifications — prefer reversible moves).

### STEP 5 — Report
Census table (per-group accounting + findings) + repair commit hashes + disposition list + **THREATS (why not to over-trust this result: skim-level verdicts, sample verification rate, denominator scope)**. If the deadline arrives first, report what exists.

### STEP 6 (opt-in, guard ⑦) — Runtime verification of top skills
Only with explicit user consent: pick the N most-used skills and run **non-destructive smokes** (`--help`, `--dry-run`, status modes, dependency version checks) into a PASS/FAIL table. Never execute destructive paths (paid APIs, outbound sends, deletions).

## Safety boundaries

- Workers never modify files — all edits are applied centrally by the main agent.
- Files owned by someone else (another agent, another person): notify via the disposition list instead of editing.
- In shared trees, `git add` by explicit filename only (never bulk-add).
- Process cleanup only after per-process tree inspection — never kill by name pattern (the origin run nearly killed three *live agent sessions* that matched a worker-looking pattern).

## Composes with

- **The gates in this repo** (`hooks/`): the audit repairs what documents *say*; the gates enforce what agents *do*. A repaired rule that never fires is decoration — wire it; a firing gate built on a stale rule enforces yesterday's truth — audit it. Run both.
- **A planning pass first** (Superpowers brainstorming, Ouroboros interview, or any spec tool): decide scope/deadline/exclusions *before* touching ~250 documents — the audit's guards assume a plan exists.
- **`/doctor` (Claude Code built-in)**: doctor checks the *installation* (settings parse, duplicate installs, unused extensions); harness-audit checks the *content* (whether your documents tell the truth). Different layers, same morning.
