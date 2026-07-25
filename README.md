# tofu-harness (formerly `tofable`)

> 🇰🇷 **한국어 버전: [README.ko.md](README.ko.md)**

**Keep an AI-agent harness honest — transfer a strong model's working style (rules + verification gates + a benchmark), and audit the harness documents themselves so they keep telling the truth.**

Two pillars, one repo:

1. **Transfer & enforce** (the original `tofable`, invoked as `/tofable`): rule layer + mechanical verification gates + the benchmark that measures whether the working style actually transfers.
2. **Audit & repair** (new, 2026-07): the [`/harness-audit` skill](skills/harness-audit/SKILL.md) — a deadline-bounded, parallel census that finds where your `CLAUDE.md` / skills / rules have drifted from reality, verifies each finding independently, and repairs only what's confirmed.

> **How this relates to [`fable-ish-codex`](https://github.com/Pandoll-AI/fable-ish-codex):** the hook design here is borrowed from that Codex plugin by Pandoll-AI (credited in [NOTICE](./NOTICE)). What `tofable` contributes on its own: **the benchmark that measures whether the harness actually transfers the working style**, and **a Claude Code port of the gates**. On Codex? The fastest path is to install the original plugin (see [`codex/`](./codex/)) — this repo is where the measurement lives.

`fable-5` here is a specific, limited-availability model — not a nickname we coined for a good run. Even over just a few days of real use, the way we worked with it settled into a genuinely good *working style*: goals decomposed honestly, work verified before "done" was claimed, blockers reported plainly instead of narrated around. Much of that style isn't in the model's weights — it lives in the habits and scaffolding built up around the model. `tofable` is an attempt to encode that scaffolding externally, as a portable harness (situational rule files + mechanical verification gates), and then **measure** how much of the working style actually transfers to other — often cheaper — models (e.g. a `sonnet`-class model) once the harness is switched on.

This repo is the public, generalized distribution of that harness. Internal names, paths, and identifiers from the environment it was developed in have been stripped; the logic and the measurement methodology have not.

![Auditing a harness: scanning agent documents for dead links and stale labels, gates passing only verified repairs](./assets/hero-harness-audit.png)

## New: audit your harness against a new model's principles

**Claude Opus 5 shipped on 2026-07-24** ([TechCrunch](https://techcrunch.com/2026/07/24/anthropic-launches-opus-5/) · [Axios](https://www.axios.com/2026/07/24/anthropic-releases-new-model-opus-5)) — and with it, Anthropic's own guidance on how a harness should be written. Two first-party documents are what the audit behind this skill was actually run against: the official [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5) guide (verification instructions cause over-verification; minimizers like "only report high-severity" shrink output literally — report everything, filter downstream) and [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models) (Anthropic blog — the post that also ships `/doctor`). The table below follows a community digest that condensed this guidance into 7 checkable principles ([@nextcocoai on Threads](https://www.threads.com/@nextcocoai/post/DbNuHBnlBrW)) — used here as a cross-check, with the author's own caveat "I'm not an expert — verify everything" applied and our verification notes included:

| # | Principle (digest) | Check it against your harness |
|---|---|---|
| 1 | Don't write what the model already does (verify/re-check instructions duplicate built-in behavior) | ⚠️ **Partially** — delete *generic* "double-check" lines, but keep gates born from real regressions: our audit found the model repeatedly *not* doing the thing the rule enforces. Rule of thumb: no incident history behind it → delete candidate; incident history → keep |
| 2 | Only specify the four things models don't self-regulate: response length, reporting cadence, document length, delegation ceiling | ✅ good entry question for every new rule (retrofit existing docs next-touch only) |
| 3 | Positive examples over prohibitions | ✅ for style rules; prohibitions still earn their keep when they block one exact failure path |
| 4 | No minimizers ("only the serious ones") — collect everything, filter in a second stage | ✅ this is literally how `/harness-audit`'s two-stage verify works (collect everything, then independent re-verification) |
| 5 | Stop scope creep — "exactly the requested scope", halt before clearly out-of-scope actions | ✅ the skill's guards ①–③ exist because of this failure mode |
| 6 | Give the full spec up front, then leave it alone; approval gates only for hard-to-reverse actions | ✅ matches the autonomy pricing this repo's rules use |
| 7 | Long files: repeat a 2–3 line reminder at the end | 🧪 worth an experiment — long-prompt dilution is real |

`/harness-audit` is the systematic version of "go check": census every harness document on four axes (tool-mismatch · stale · dead-link · conflict), re-verify findings with independent workers, repair only what's confirmed — inside a deadline. In its origin run (a single overnight pass, one harness, 252 documents) it confirmed 49 defects and repaired **all of them** — one commit spanning 47 files, plus 2 sibling fixes. Those counts carry their scope label on purpose: per-document verdicts, not aggregates, are the reliable unit (see the STEP 2 note in the skill).

**How the pieces fit together** (use all four, they cover different layers):

| Layer | Tool | Question it answers |
|---|---|---|
| Plan | Superpowers brainstorming / Ouroboros interview / any spec tool | *What* should change, in what scope, by when — decide **before** touching ~250 files |
| Installation | Claude Code's built-in `/doctor` | Is the *setup* healthy — settings parse, duplicate installs, unused extensions |
| Documents | **`/harness-audit`** (this repo) | Do your harness documents *tell the truth* about tools, paths, models, and each other |
| Behavior | **the gates** (`hooks/`, this repo) | Does the agent actually *do* what the documents say — mechanically, at Stop/PreToolUse time |

A repaired rule that never fires is decoration — wire it (gates). A firing gate built on a stale rule enforces yesterday's truth — audit it (skill). Plan first so neither eats your night; run `/doctor` so you're not auditing a broken install.

**Usage** (friendly version):

```
1. Tell your agent:  "run harness-audit, deadline 2 hours, scope: this project + my home config"
2. It declares 3 deliverables (census table · repair commits · disposition list) and fixes the file list first
3. Parallel workers judge every document on 4 axes  →  different workers re-verify each finding from scratch
4. Only CONFIRMED findings get repaired, centrally, with unique-match safety; everything else lands in the disposition list
5. Optional (it will ask): non-destructive runtime smokes of your most-used skills
```

## Start here

| You are… | Do this |
|---|---|
| on **Claude Code**, want the verification gate | copy [`hooks/`](hooks/) and follow the [step-by-step install](hooks/README.md) (~5 min), then seed your rule layer from the examples in [`rules/`](rules/) |
| on **Codex** | install the upstream plugin [`fable-ish-codex`](https://github.com/Pandoll-AI/fable-ish-codex) instead — see [`codex/README.md`](codex/README.md) |
| here to **measure** whether a harness actually transfers a working style | start at [Key finding](#key-finding) below, then run [`bench/`](bench/) against your own model |
| here because **a new model just shipped** and your harness may be stale | read [`skills/harness-audit/SKILL.md`](skills/harness-audit/SKILL.md) and run it with a deadline |

![infographic](./docs/infographic-en.png)

## Key finding

We ran the same task set on two comparable models (`fable-5` and `sonnet-5`), **both without the harness** — a vanilla control arm (a scratch working dir where the house rules aren't loaded). The tasks split cleanly into two kinds:

| Task category | Example tasks | Vanilla avg score |
|---|---|---|
| **Harness-dependent** — the correct answer lives in a specific written house rule, not in general competence | deck-outline-before-build, image-edit-vs-generate, research-delegation | **~62** |
| **General-reasoning** — competent models get these right regardless of house rules | fact-check, cardnews, knowledge-save, writing | **~90** |

**The ~28-point gap is what turning the harness ON is expected to recover.** It isolates the part of "the model didn't do what we wanted" that is actually an *instruction-coverage* problem (the model never saw the rule) rather than a *capability* problem (the model can't reason well enough). Harness-dependent tasks are exactly the ones a rules-and-gates system is supposed to fix; general-reasoning tasks are a control group showing the same model is otherwise fine.

Two more findings from the same measurement pass, because they change how you should read any "harness helped" number:

- **A written rule is not enforcement.** The ported verification gate (the `Stop`-hook pattern described in [docs/method.md](docs/method.md)) actually blocked its own author's session mid-task. That's not a bug report — it's the proof that the gate was mechanically live rather than decorative documentation. If a rule never fires, you don't actually know it's wired in.
- **Some of the score gap is an instrument gap, not a model gap.** Simply preserving tool-use transcripts (evidence of what commands actually ran) instead of grading on the model's self-report raised the hard-security benchmark from 93 to 96 — the earlier lower score was largely the grader being unable to see work the model had actually done, not the model failing to do it.

### Scoreboard (Cycle 1 — vanilla / harness off)

| Benchmark | fable-5 | sonnet-5 |
|---|---:|---:|
| core-3 | 89.9 | 86.7 |
| hard-security | 96.5 | 95.2 |
| real-work-7 | 79.3 | 75.3 |

### Where `fable` and a comparable model differ — and why

Both columns are the vanilla arm (no harness loaded), so the `fable-5` vs `sonnet-5` gap here is the two models' *raw* difference, before any harness — the useful question is *where* they diverge and *on what evidence*. The gap is not uniform:

- **It concentrates in judgment-heavy tasks.** Orchestration: **96.3 (clean)** vs **88.3 (P1)** — `fable-5` put a *hard gate* on a low-context worker (block-until-resolved + reassign) where the comparable model allowed "proceed if cleanup is hard," a skipped discipline. Constrained writing: **93.3** vs **76.7 (P1)** — `fable-5` honored a "no outside references" rule the other broke.
- **It nearly vanishes or reverses on mechanical tasks.** On plain secret-scan and code-fix, the comparable model *ties or beats* `fable-5` — at **~2.5–3× lower cost**.

The honest, evidence-backed read: **`fable-5`'s edge is judgment under ambiguity — gating a risky step, honoring a constraint, auditing more thoroughly — not a uniform lift.** You'd route mechanical work to the cheaper model. Per-task evidence for every one of these claims is in [`bench/results.md`](bench/results.md).

**How scoring works** (the cycle-1 numbers above were scored under rubric v1 — six axes, A1–A5 plus a task-specific SPECIAL, with P0/P1 defect gates, judged on the actual tool-use transcript; the rubric is now **v2**, adding process axes A6–A8 for planning/continuity/work-product quality) and the full **per-task results** are in [`bench/results.md`](bench/results.md); the axes/anchors are in [`bench/rubric.md`](bench/rubric.md) and the judging procedure in [`bench/judge-prompt.md`](bench/judge-prompt.md).

## The gates — and what they measurably change

![The gate set inspecting work before it passes](./assets/hero-gates.png)

The single most reproduced finding across our measurement cycles: **a written rule is not enforcement.** Models (especially cheaper ones) skim past prose rules, but they cannot skim past a hook that bounces their Stop. So the harness's active ingredient is the gate set:

| Gate | Fires | Catches |
|---|---|---|
| `verify-ledger` | after every tool call | nothing — it *records* what changed and what was verified (the evidence the other gates judge) |
| `stop-verify-gate` | on Stop | code/config changed, but no successful verification ran *after* the change |
| — absence check | on Stop | "X doesn't exist" claimed after consulting git shallowly (no `--all` / `branch -a` boundary expansion) |
| — claim-evidence check | on Stop | a precise count ("83 messages") or an identity claim ("byte-for-byte identical") with no mechanical check (`wc -l`, `grep -c`, `diff`, `shasum`) in the tool log |
| — subordinate-evidence check | on Stop | completion declared after delegating to a subagent, with no verification recorded *after* the delegate returned — a delegate's "done" is a claim, not evidence |
| `continuation-gate` | on Stop | deferral language ("I'll continue tomorrow") while work remains and nothing is user-blocked |
| `surfacing-gate` | before Bash | a destructive command (recursive rm, force-push, hard reset) about to run **silently** — the gate blocks it once and requires the reply to surface what is being destroyed and why it's safe; the surfaced re-run passes |
| `blind-retry-gate` | before Bash | re-running the **byte-identical command that just failed** — the gate blocks it once ("An error is data — read it before spending another attempt"); a diagnosed or changed command passes immediately |
| `prompt-advance-gate` | before Write/Edit/Task (+MultiEdit/Agent) | execution starting right after an interview / brainstorm / plan phase **with no prompt-engineering pass** in between — bounced once per session; pairs with a `/prompt`-style skill (see below) |

Every gate bounces **once**, always has a path through (show the evidence, or state explicitly why it's impossible), and fails open — a broken gate never wedges a session. Nothing is hard-forbidden by design: gates demand evidence, they don't ban actions — the "Catches" column above describes the failure pattern each gate *intercepts*, not something the gate performs. Kill switch: `FABLE_GATE_OFF=1`.

The prompt-engineering pass that `prompt-advance-gate` looks for is any deliberate prompt-crystallization step between planning and execution. Our reference implementation is the **[prompt-engineering-skills](https://github.com/treylom/prompt-engineering-skills)** repo (`/prompt` — model-routed prompt generator; its AUTO mode runs one self-critique pass and executes immediately, built for autonomous agent flows where waiting on a human option-pick would stall the pipeline). Any equivalent skill satisfies the gate — it detects the pass generically, not that specific repo.

**Ledger v5.2 (measured friction repairs).** After a week of running the gates live across a multi-agent fleet, we labeled every real block (94 of them) as true-positive, false-positive, or friction — and repaired the friction patterns instead of weakening the gates: stop-verify now names only paths changed since the last successful verification and never re-bounces the same unverified set twice; surfacing-gate's one-shot pass survives a benign re-wording of the same command when the destructive token *and* the target overlap (a different target still surfaces on its own); and the workflow-reminder gate was narrowed to substantial solo starts after measuring a near-zero value ratio in meeting-driven sessions. Each repair began as a failing test reproducing the measured friction (`hooks/tests/test_weight_audit_repairs.py`).

The two newest checks (subordinate-evidence, blind-retry) were mined from the source model's actual work logs cross-referenced against a 68-incident failure corpus — they cover the two worst-recurrence axes (trusting a delegate's unverified "done"; re-attacking an error with the identical command). Their unit contracts are tested; their bench effect is the next measurement cycle, so the table below does not include them yet.

**Measured effect** (14 fixtures × 2–3 seeds per arm; *composite* = avg − 15·P0 − 5·P1 per fixture cell, so defects can't hide behind style points):

| Arm | avg | composite | P0 | P1 |
|---|---:|---:|---:|---:|
| `sonnet-5` vanilla | 89.1 | 86.2 | 1 | 5 |
| `sonnet-5` + tofable | **90.7** | **89.6** | **0** | **3** |
| `opus`-class vanilla | 90.0 | 88.5 | 0 | 4 |
| `opus`-class + tofable | 90.8 | 89.7 | 0 | 3 |

Fixture-level, the gains sit exactly where a gate was added: the absence-claim trap went **75.6 → 96.3** (absence check), the counting trap **87.9 → 94.2** (claim-evidence check), and the vanilla arm's one fabrication-class P0 (inventing figures for a public post) disappeared under the harness. (These traps are separate fixtures from the harness-dependent bucket above — gate gains concentrate on the gated traps and get diluted in the 14-fixture average; recovery of the ~62 bucket is measured separately in [`bench/results.md`](bench/results.md).) On the stronger model the same gates cost nothing and help slightly — avg 90.0 → 90.8, composite 88.5 → 89.7, P1 4 → 3 — models that already have the habit pass through silently; models that don't get corrected. That asymmetry is the design intent, and it produces the headline: **the harnessed cheaper model lands within 0.1 composite of the harnessed stronger one, at roughly three-quarters of the cost.**

Two honest footnotes from the same pass. A *compact* variant of the rule files (same content, ~40% shorter) scored the same average with **more** defects — brevity is not enforcement either; the gates are what move behavior. And one judge false-positive taught us to attach fixture **input materials** to the judge, not just the answer key — a graded model was flagged for "fabricating" strings that were verbatim in its source file. The improvement loop this repo runs is exactly: defect readout → new gate → re-bench. Two cycles so far have reproduced the same exchange rate — **one gate ≈ one defect axis removed** — with the usual small-n caveat (2–3 seeds per cell, ±10-point per-fixture noise; read arm averages, not single cells).

## Weigh your gates: the audit loop

![An inspector robot weighing each gate on a scale, passing the ones that earn their keep](./assets/hero-audit.png)

The obvious worry about a gate harness is weight: *isn't all this checking making the agent slower and noisier?* We stopped speculating and measured it — a full week of live transcripts across a 9-agent fleet, every real gate event extracted and labeled by reading what the agent did next. The answer flipped the intuition twice:

- **Per-gate cost is noise** (16–30ms per hook; the real cost is a bounced turn), so **the speed KPI of a gate system is its false-positive rate** — and the verification gates measured roughly 70–100% true-positive. The fixes that made the fleet faster were false-positive repairs (ledger v5.2 above), not gate removals.
- **"Which gates should this agent run?" is a classification question, not a preference.** Content-triggered gates (destructive commands, unverified counts, completion claims) are self-scoping and belong everywhere; only genuinely bot-exclusive gates deserve per-agent guards; and headless/cron sessions need an explicit automation carve-out — with the exact env var each hook layer actually reads (we found a documented one that no layer implemented).

The whole procedure is packaged to rerun on your own fleet:

- **[`docs/gate-audit-playbook.md`](docs/gate-audit-playbook.md)** — the five steps (inventory → measure → label → rank → per-agent set), each with the trap we actually fell into before finding the working method (name-grep contamination, silent-pass invisibility, log-vs-transcript double counting, cwd-scoped settings that quietly apply your "shared" hooks to exactly one agent).
- **[`scripts/audit/scan_gate_events.py`](scripts/audit/scan_gate_events.py)** — the real-event scanner (Stop-feedback / error-deny discriminators, not gate-name grep).
- **[`profiles/gate-profiles.json`](profiles/gate-profiles.json)** — per-agent profiles (orchestrator / generalist / research / writing / schedule-automation / pipeline / visual / codex): pick one at install time and wire only its groups. Profiles select *wirings*; gate code and rule text stay single-source — forking them per agent is the #1 drift failure mode.

## Repo structure

```
tofu-harness/
├── README.md            — this file
├── LICENSE               — MIT (this repo's own contributions)
├── NOTICE                — Apache-2.0 attribution for the ported hook design
├── docs/
│   ├── method.md          — the transfer method: rule patterns, verification ledger/stop-gate, benchmark loop, mining loop
│   ├── gate-audit-playbook.md — the audit loop: decide which gates each agent actually needs, with measurements
│   └── infographic-en.png / infographic-ko.png  — summary graphics (en / ko; source: infographic-src.html — edit text + re-render to refresh)
├── skills/
│   └── harness-audit/     — the audit skill: census → independent re-verify → central repair (7 guards)
├── rules/                 — copyable example rule layer (situation index + trigger-keyed rule files)
├── hooks/                 — harness-agnostic, generalized verification hooks (evidence ledger + stop-gate)
│   ├── requirements-lock.py   — opt-in completion-bias guard (locked feature signatures must keep existing)
│   └── tests/
│       ├── replay/            — violation corpus: past gate-worthy violations replayed as fixtures (block rate + corpus floor)
│       └── probes/            — practice probes: the gate pipeline's own contracts, checked deterministically
├── profiles/
│   └── gate-profiles.json — per-agent gate profiles: pick a domain profile, wire only its groups
├── scripts/audit/
│   └── scan_gate_events.py — real-gate-event scanner for the audit loop (docs/gate-audit-playbook.md)
├── assets/                — README illustrations
├── bench/                 — the harness-dependent vs. general-reasoning task set, scoring, and raw results
│   └── substrate-check.sh     — one-line substrate snapshot for model-transition rehearsals (before/after delta must be 0)
└── codex/
    └── README.md          — how to use this with Codex, via the upstream fable-ish-codex plugin
```

## Quickstart

**1. Seed the rule layer.**

Copy [`rules/`](rules/) into your harness workspace (e.g. `.claude/rules/`), point your always-loaded prompt at the index, and start replacing the example rows with your own house rules — one situation per file. The design rationale (why an index instead of front-loading, why rules must cite incidents) is in [`rules/README.md`](rules/README.md).

**2. Install the hooks into your harness.**

`hooks/` is the generalized, harness-agnostic form of the verification lifecycle. The core three:

- **`fable_lib.py`** — shared library. A "harness/code surface" heuristic decides which changed files require verification evidence (plain notes/markdown are exempt); an append-only evidence ledger records verifications, git usage, and boundary-expansion evidence (kept outside the project tree so it's never committed); and a pilot-gate kill switch (`FABLE_GATE_OFF=1`, or `FABLE_GATE_PILOT=<name>` to scope the gate to one named session before enabling it broadly). The other hooks import it.
- **`verify-ledger.py`** — a `PostToolUse(Write|Edit|Bash)` hook. After a tool call, if the action is a real verification (a test run, a scan, a cross-check) it records that as evidence in an ordered ledger. It only records — never blocks. Fail-open (any exception exits cleanly).
- **`stop-verify-gate.py`** — a `Stop` hook carrying three checks (see [the gates table](#the-gates--and-what-they-measurably-change) above): change-verification, the absence-claim check, and the claim-evidence check. Each emits `{"decision":"block"}` to bounce the stop once with a concrete checklist. Capped bounces, loop-guard aware, fail-open — a broken hook never wedges a session.

Alongside them: **`continuation-gate.py`** (Stop — deferral language), **`surfacing-gate.py`** (PreToolUse — destructive-command surfacing), and the opt-in **`cutover-review-gate.py`** / **`requirements-lock.py`** / **`branch-stray-guard.sh`** described in their headers.

Wire `verify-ledger.py` into your harness's post-tool-use event and `stop-verify-gate.py` into its stop / turn-end event; both import `fable_lib.py`. **[`hooks/README.md`](hooks/README.md) has the step-by-step Claude Code install** — the exact `settings.json` snippets, how to confirm the gate is live, and the kill switch. After wiring, run `hooks/tests/test_gate.py` — it's a runnable spec of the gate's contract. Two companion suites keep the gate honest over time: `hooks/tests/replay/run.py` replays archived violation scenarios (block rate must stay 100%, and a corpus floor stops fixture-deletion from faking it), and `hooks/tests/probes/run.py` checks the pipeline's own contracts (exit-code conventions, ledger schema, escape hatches). When you switch reasoning models, `bench/substrate-check.sh` snapshots all of it in one JSON line — run it before and after; delta 0 confirms the gate mechanics (block rate, contracts, hooks) are intact across the transition — the plumbing didn't break. Behavioral transfer is what `bench/` measures. Adoption reasoning for these pieces: [docs/decision-history.md](docs/decision-history.md). If your harness is Codex specifically, see [Codex integration](#codex-integration) below — you likely want the upstream plugin instead of a manual port.

**3. Run the benchmark.**

```bash
# run one fixture against one model, preserving the full tool-use transcript
bench/run.sh example-codefix <your-model-id> my-run

# artifacts land in $FABLE_BENCH_RUNS_DIR (default ~/.fable-bench/runs/):
#   work/  transcript.jsonl  raw-output.json  meta.json
```

Then grade the run with a judge — ideally a **different model family** than the one that produced it — feeding it `bench/rubric.md` + the fixture's answer key + the run's transcript, via the template in `bench/judge-prompt.md`. Full runner options, how scoring is assembled, and the fixture-authoring / runtime-trap pattern are in [`bench/README.md`](bench/README.md) and [`bench/results.md`](bench/results.md).

The benchmark runs the same task set with the harness off (vanilla) and on, and reports the harness-dependent vs. general-reasoning split described above. Use it to check whether *your* harness install actually recovers the gap on *your* base model — the numbers above are one measurement, not a universal constant.

## Codex integration

If you're on Codex, prefer installing the upstream plugin this project's hook design was adapted from — `fable-ish-codex` (Apache-2.0, Pandoll-AI) — rather than manually porting `hooks/`. See [`codex/README.md`](codex/README.md) for install steps and how the two projects relate.

## Method

The full write-up of the transfer method — rule-pattern design, the verification ledger / stop-gate mechanism, the benchmark loop used to measure transfer, and the mining loop that keeps the rule layer growing from real sessions — is in [`docs/method.md`](docs/method.md).

## Acknowledgments

This project stands on work generously shared by others in the Korean Claude/Codex community:

- **[fablize](https://github.com/fivetaku/fablize)** by gptaku ([@gptaku_ai](https://www.threads.com/@gptaku_ai)) — a Claude Code plugin making Opus behave like Fable, with completion/evidence/verification enforced as procedure. A parallel take on the same transfer problem that sharpened ours.
- **[fable-ish-codex](https://github.com/Pandoll-AI/fable-ish-codex)** by voice / 현님 ([@voidlight00](https://www.threads.com/@voidlight00), Pandoll-AI, Apache-2.0) — the upstream this project's hook design was adapted from (see NOTICE).
- **[Hugh Kim](https://github.com/jung-wan-kim)** ([@hue_0525](https://www.threads.com/@hue_0525), [hugh-kim.space](https://hugh-kim.space)) — the fable-week series ([day 1](https://hugh-kim.space/fable-week.html), [day 2](https://hugh-kim.space/fable-week-2.html)), whose completion-gate / closed-loop / honest-measurement benchmarks this repo borrows as its evaluation frame.

Thank you — this repo would be thinner without each of you.

## License

This repository's own contributions are licensed under the [MIT License](LICENSE). The hook design under `hooks/` is adapted from `fable-ish-codex` (Apache-2.0, Copyright Pandoll-AI); see [NOTICE](NOTICE) for the required attribution.
