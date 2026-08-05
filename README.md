# tofu-harness (formerly `tofable`)

> 🇰🇷 **한국어 버전: [README.ko.md](README.ko.md)**

**Keep an AI-agent harness honest.** Transfer a working style into rules and mechanical gates, then audit the harness documents themselves so they keep telling the truth about your tools, paths, and models.

![Auditing a harness: scanning agent documents for dead links and stale labels, gates passing only verified repairs](./assets/hero-harness-audit.png)

## Two pillars

| | Skill | What it does |
|---|---|---|
| **Transfer & enforce** | `/tofable` | A copyable rule layer plus verification gates that bounce a turn when evidence is missing. The original half of this repo. |
| **Audit & repair** | `/harness-audit` | A deadline-bounded census of your harness documents — finds where `CLAUDE.md` / skills / rules have drifted from reality, re-verifies each finding independently, repairs only what's confirmed. Added 2026-07. |

Plugin packaging is **skill-only**. The gates under [`hooks/`](hooks/) install separately — see [`hooks/README.md`](hooks/README.md).

## Start here

| You are… | Do this |
|---|---|
| here because **a new model just shipped** and your harness may be stale | run [`/harness-audit`](skills/harness-audit/SKILL.md) with a deadline |
| on **Claude Code**, want the verification gates | copy [`hooks/`](hooks/), follow the [step-by-step install](hooks/README.md) (~5 min), seed rules from [`rules/`](rules/) |
| on **Codex** | install the upstream plugin [`fable-ish-codex`](https://github.com/Pandoll-AI/fable-ish-codex) — see [`codex/README.md`](codex/README.md) |
| here to **measure** whether a harness transfers a working style | run [`bench/`](bench/) against your own model; results and method in [`bench/results.md`](bench/results.md) |

### Install

```
claude plugin marketplace add treylom/tofu-harness
/plugin install tofu-harness@tofu-harness
```

Updating later:

```
claude plugin marketplace update tofu-harness
claude plugin update tofu-harness@tofu-harness
```

---

## `/harness-audit` — does your harness still tell the truth?

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

**Usage:**

```
1. Tell your agent:  "run harness-audit, deadline 2 hours, scope: this project + my home config"
2. It declares 3 deliverables (census table · repair commits · disposition list) and fixes the file list first
3. Parallel workers judge every document on 4 axes  →  different workers re-verify each finding from scratch
4. Only CONFIRMED findings get repaired, centrally, with unique-match safety; everything else lands in the disposition list
5. Optional (it will ask): non-destructive runtime smokes of your most-used skills
```

**Where it sits among your other tools** — four layers, four different questions:

| Layer | Tool | Question it answers |
|---|---|---|
| Plan | Superpowers brainstorming / Ouroboros interview / any spec tool | *What* should change, in what scope, by when — decide **before** touching hundreds of files |
| Installation | Claude Code's built-in `/doctor` | Is the *setup* healthy — settings parse, duplicate installs, unused extensions |
| Documents | **`/harness-audit`** | Do your harness documents *tell the truth* about tools, paths, models, and each other |
| Behavior | **the gates** (`hooks/`) | Does the agent actually *do* what the documents say — mechanically, at Stop/PreToolUse time |

A repaired rule that never fires is decoration — wire it (gates). A firing gate built on a stale rule enforces yesterday's truth — audit it (skill). Plan first so neither eats your night; run `/doctor` so you're not auditing a broken install.

---

## `/tofable` — the gates

The single most reproduced finding across our measurement cycles: **a written rule is not enforcement.** Models skim past prose rules; they cannot skim past a hook that bounces their Stop. So the harness's active ingredient is the gate set:

| Gate | Fires | Catches |
|---|---|---|
| `verify-ledger` | after every tool call | nothing — it *records* what changed and what was verified (the evidence the other gates judge) |
| `stop-verify-gate` | on Stop | code/config changed, but no successful verification ran *after* the change |
| — absence check | on Stop | "X doesn't exist" claimed after consulting git shallowly (no `--all` / `branch -a` boundary expansion) |
| — claim-evidence check | on Stop | a precise count or an identity claim ("byte-for-byte identical") with no mechanical check (`wc -l`, `grep -c`, `diff`, `shasum`) in the tool log |
| — subordinate-evidence check | on Stop | completion declared after delegating to a subagent, with no verification recorded *after* the delegate returned — a delegate's "done" is a claim, not evidence |
| `continuation-gate` | on Stop | deferral language ("I'll continue tomorrow") while work remains and nothing is user-blocked |
| `surfacing-gate` | before Bash | a destructive command (recursive rm, force-push, hard reset) about to run **silently** — blocked once; the reply must surface what is being destroyed and why it's safe |
| `blind-retry-gate` | before Bash | re-running the **byte-identical command that just failed** — blocked once ("An error is data — read it before spending another attempt") |
| `prompt-advance-gate` | before Write/Edit/Task | execution starting right after an interview / brainstorm / plan phase **with no prompt-engineering pass** in between |

Every gate bounces **once**, always has a path through (show the evidence, or state why it's impossible), and fails open — a broken gate never wedges a session. Gates demand evidence; they don't ban actions. Kill switch: `FABLE_GATE_OFF=1`.

The prompt-engineering pass that `prompt-advance-gate` looks for is any deliberate prompt-crystallization step between planning and execution. Our reference implementation is [prompt-engineering-skills](https://github.com/treylom/prompt-engineering-skills) (`/prompt`), but the gate detects the pass generically — any equivalent skill satisfies it.

### Does it actually help?

Yes, measurably — but read the scope label before you carry the numbers anywhere.

> ⚠️ **These measurements are from an earlier model generation** (`fable-5` / `sonnet-5` class, cycles 1–2, 2–3 seeds per cell). **Opus 5 and its siblings will behave differently** — a stronger model needs fewer of these corrections, so expect the *size* of the effect to shrink even where the direction holds. Treat the numbers as evidence that the method works, not as a constant to expect on your own setup. Full per-task results, rubric, and raw runs: **[`bench/results.md`](bench/results.md)**.

The three findings worth carrying forward, all of which survive the generation caveat:

- **The gap the harness targets is instruction-coverage, not capability.** With the harness off, tasks whose correct answer lives in a specific written house rule scored ~30 points below tasks a competent model gets right regardless. That gap is what a rules-and-gates system exists to recover — and it isolates "the model never saw the rule" from "the model can't reason well enough."
- **The gains land exactly where a gate was added.** Fixture-level, the absence-claim trap and the counting trap both jumped once their gates existed, while the overall average barely moved — gate gains concentrate on gated traps and get diluted in a broad average. One gate ≈ one defect axis removed, reproduced across two cycles.
- **Brevity is not enforcement.** A compact variant of the rule files (same content, ~40% shorter) scored the same average with *more* defects. Shortening prose doesn't make it bind; only the gates moved behavior.

Two honest footnotes. Some of what looks like a model gap is an **instrument** gap — grading on preserved tool-use transcripts instead of the model's self-report raised one benchmark by three points without the model doing anything differently. And one judge false-positive taught us to attach fixture *input materials* to the judge, not just the answer key.

### Keeping the gates honest

After a week of live use across a multi-agent fleet, we labeled every real gate event (94 of them) as true-positive, false-positive, or friction — and repaired the friction patterns instead of weakening the gates. Two results flipped our intuition:

- **Per-gate cost is noise** (16–30ms per hook; the real cost is a bounced turn), so **the speed KPI of a gate system is its false-positive rate** — measured roughly 70–100% true-positive. What made the fleet faster was false-positive repair, not gate removal.
- **"Which gates should this agent run?" is a classification question, not a preference.** Content-triggered gates (destructive commands, unverified counts, completion claims) are self-scoping and belong everywhere; only genuinely bot-exclusive gates deserve per-agent guards; headless/cron sessions need an explicit automation carve-out.

The procedure is packaged to rerun on your own fleet: [`docs/gate-audit-playbook.md`](docs/gate-audit-playbook.md) (five steps, each with the trap we fell into first), [`scripts/audit/scan_gate_events.py`](scripts/audit/scan_gate_events.py) (real-event scanner, not gate-name grep), and [`profiles/gate-profiles.json`](profiles/gate-profiles.json) (per-agent profiles — profiles select *wirings*; gate code stays single-source, since forking it per agent is the #1 drift failure mode).

---

## Quickstart

**1. Seed the rule layer.** Copy [`rules/`](rules/) into your harness workspace (e.g. `.claude/rules/`), point your always-loaded prompt at the index, and replace the example rows with your own house rules — one situation per file. Design rationale in [`rules/README.md`](rules/README.md).

**2. Install the hooks.** The core three:

- **`fable_lib.py`** — shared library: decides which changed files require verification evidence, maintains an append-only evidence ledger (kept outside the project tree so it's never committed), and holds the kill switch (`FABLE_GATE_OFF=1`, or `FABLE_GATE_PILOT=<name>` to scope the gate to one session first).
- **`verify-ledger.py`** — `PostToolUse(Write|Edit|Bash)`. Records real verifications as evidence. Never blocks. Fail-open.
- **`stop-verify-gate.py`** — `Stop`, carrying three checks (change-verification, absence-claim, claim-evidence). Bounces once with a concrete checklist. Capped, loop-guard aware, fail-open.

Alongside them: `continuation-gate.py`, `surfacing-gate.py`, and the opt-in `cutover-review-gate.py` / `requirements-lock.py` / `branch-stray-guard.sh`.

**[`hooks/README.md`](hooks/README.md) has the step-by-step Claude Code install** — exact `settings.json` snippets, how to confirm the gate is live, and the kill switch. After wiring, run `hooks/tests/test_gate.py` (a runnable spec of the gate's contract). Two companion suites keep it honest: `hooks/tests/replay/run.py` replays archived violations (block rate must stay 100%, with a corpus floor so fixture deletion can't fake it) and `hooks/tests/probes/run.py` checks pipeline contracts. When switching reasoning models, `bench/substrate-check.sh` snapshots all of it in one JSON line — run before and after; delta 0 confirms the plumbing survived the transition.

**3. Run the benchmark.**

```bash
# run one fixture against one model, preserving the full tool-use transcript
bench/run.sh example-codefix <your-model-id> my-run

# artifacts land in $FABLE_BENCH_RUNS_DIR (default ~/.fable-bench/runs/):
#   work/  transcript.jsonl  raw-output.json  meta.json
```

Grade the run with a judge — ideally a **different model family** than the one that produced it — feeding it `bench/rubric.md` + the fixture's answer key + the run's transcript, via `bench/judge-prompt.md`. The benchmark runs the same task set with the harness off and on, so you can check whether *your* install recovers the gap on *your* base model.

## Repo structure

```
tofu-harness/
├── README.md              — this file
├── LICENSE                — MIT (this repo's own contributions)
├── NOTICE                 — Apache-2.0 attribution for the ported hook design
├── docs/
│   ├── method.md              — the transfer method: rule patterns, ledger/stop-gate, benchmark loop, mining loop
│   ├── gate-audit-playbook.md — the audit loop: which gates each agent actually needs, with measurements
│   └── decision-history.md    — adoption reasoning for the pieces above
├── skills/
│   ├── tofable/           — the working-discipline skill (`/tofable`)
│   └── harness-audit/     — the audit skill (`/harness-audit`): census → independent re-verify → central repair (7 guards)
├── rules/                 — copyable example rule layer (situation index + trigger-keyed rule files)
├── hooks/                 — harness-agnostic verification hooks (evidence ledger + stop-gate); installs separately
│   └── tests/
│       ├── replay/            — violation corpus replayed as fixtures (block rate + corpus floor)
│       └── probes/            — the gate pipeline's own contracts, checked deterministically
├── profiles/
│   └── gate-profiles.json — per-agent gate profiles: pick a domain profile, wire only its groups
├── scripts/audit/
│   └── scan_gate_events.py — real-gate-event scanner for the audit loop
├── assets/                — README illustrations
├── bench/                 — the task set, scoring, and raw results
│   └── substrate-check.sh — one-line substrate snapshot for model-transition rehearsals
└── codex/
    └── README.md          — how to use this with Codex, via the upstream fable-ish-codex plugin
```

## What this repo is, and where it came from

`fable-5` here is a specific, limited-availability model — not a nickname we coined for a good run. Over real use, the way we worked with it settled into a genuinely good *working style*: goals decomposed honestly, work verified before "done" was claimed, blockers reported plainly instead of narrated around. Much of that style isn't in the model's weights — it lives in the habits and scaffolding built around the model. This repo encodes that scaffolding externally, as a portable harness, and then **measures** how much of the style actually transfers to other — often cheaper — models once the harness is on.

This is the public, generalized distribution of that harness. Internal names, paths, and identifiers from the environment it was developed in have been stripped; the logic and the measurement methodology have not.

**How this relates to [`fable-ish-codex`](https://github.com/Pandoll-AI/fable-ish-codex):** the hook design here is borrowed from that Codex plugin by Pandoll-AI (credited in [NOTICE](./NOTICE)). What this repo contributes on its own: **the benchmark that measures whether the harness actually transfers the working style**, and **a Claude Code port of the gates**. On Codex, the fastest path is the original plugin — see [`codex/`](./codex/).

The full write-up of the transfer method is in [`docs/method.md`](docs/method.md).

## Acknowledgments

This project stands on work generously shared by others in the Korean Claude/Codex community:

- **[fablize](https://github.com/fivetaku/fablize)** by gptaku ([@gptaku_ai](https://www.threads.com/@gptaku_ai)) — a Claude Code plugin making Opus behave like Fable, with completion/evidence/verification enforced as procedure. A parallel take on the same transfer problem that sharpened ours.
- **[fable-ish-codex](https://github.com/Pandoll-AI/fable-ish-codex)** by voice / 현님 ([@voidlight00](https://www.threads.com/@voidlight00), Pandoll-AI, Apache-2.0) — the upstream this project's hook design was adapted from (see NOTICE).
- **[Hugh Kim](https://github.com/jung-wan-kim)** ([@hue_0525](https://www.threads.com/@hue_0525), [hugh-kim.space](https://hugh-kim.space)) — the fable-week series ([day 1](https://hugh-kim.space/fable-week.html), [day 2](https://hugh-kim.space/fable-week-2.html)), whose completion-gate / closed-loop / honest-measurement benchmarks this repo borrows as its evaluation frame.

Thank you — this repo would be thinner without each of you.

## License

This repository's own contributions are licensed under the [MIT License](LICENSE). The hook design under `hooks/` is adapted from `fable-ish-codex` (Apache-2.0, Copyright Pandoll-AI); see [NOTICE](NOTICE) for the required attribution.

## Fill-in markers (`▶ Fill in:`)

The rule files in `rules/` are generalized from a working internal setup. Everywhere a rule
depends on a value specific to YOUR deployment — a channel/thread id, a tool or script path,
a persona name, a search endpoint — the value is replaced with a `▶ Fill in:` marker.

**A rule whose marker is left blank is not a weaker rule — it is an inactive one.** In
particular, gates marked CRITICAL (e.g. the completion-report gate in `rules/autonomy.md` §2)
do not operate at all until their markers are filled: an unfilled completion-thread id means
the gate silently never fires. Treat the marker list as an installation checklist, not as
optional annotations.

Current marker counts per file (grep `▶ Fill in` to regenerate):
code-quality 18 · discord-comms 8 · skill-process 7 · autonomy 6 · image-ops 5 ·
maintenance 5 · meeting-protocol 5 · orchestration 4 · search-usage 4 · voice 3 ·
source-fact 2 · porting-infra 1 — total 68.
