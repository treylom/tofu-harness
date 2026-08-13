---
name: install-hooks
description: Use when someone asks to install this bundle's verification hooks into a project — "install the project hooks", "set up the gates here", "프로젝트 관련 훅 설치해줘". Picks the hooks that fit the harness and the project, wires them into settings, and then proves each one is actually live by making it fire. Copying files is not installing; this skill does not report success until a gate has blocked something on purpose.
---

# /install-hooks — wire the gates in, then make them fire

> Why this exists: the install used to be a README walkthrough — copy files, paste JSON, ~5 minutes. That path ends with *files in place*, and people read that as *gates active*. The two are different, and the gap is silent: a hook with a typo'd path, a matcher that never matches, or a `settings.json` the harness didn't reload will sit there looking installed forever. **This skill's terminal state is a deliberate block, not a file listing.**

## The rule

**Never report "installed" from a file copy, a `settings.json` diff, or a passing unit test.** Report it only after a gate you just wired **actually blocked a real attempt** in this session. If you cannot make it fire, say it is unverified and name which one.

## STEP 0 — Read the target before touching it

1. **Which harness?** Claude Code (`.claude/settings.json` or `~/.claude/settings.json`) vs Codex (`~/.codex/hooks.json`). They take different event names — do not assume.
2. **What is already wired?** Read the existing settings file **in full** before editing. Count the existing hook entries and write the number down; you will compare after.
3. **Is a bundle already installed?** If some of these hooks are present, this is an upgrade, not an install — diff versions rather than overwriting, and say which files you are replacing.

If the settings file does not exist, create it — but say so explicitly, because an absent file and an empty-but-present file fail differently later.

## STEP 1 — Choose what fits, and say what you skipped

Do not install everything by default. Ask what the project actually needs, or infer it and state the inference.

**Install in groups, not all at once.** The groups below are the same three names [`harness-setup`](../harness-setup/SKILL.md) uses — if you change one list, change both, or a profile will mean two different things depending on which skill ran.

| Group | Hooks | Pick this when |
|---|---|---|
| **`core`** | `fable_lib` + `verify-ledger` + `stop-verify-gate` | First install, or a shared repo where one false positive would be expensive |
| **`recommended`** | `core` + `continuation-gate` + `surfacing-gate` + `blind-retry-gate` + `prompt-advance-gate` | Your daily project — **start here if unsure** |
| **`full`** | `recommended` + every gate marked *opt-in* below | You already know which gates you want and accept the tuning cost |

The split is not invented here: **`recommended` is exactly the gates [`hooks/README.md`](../../hooks/README.md) does *not* mark opt-in, and `full` adds the ones it does.** That file is the inventory of record — if a gate is added there, it lands in `full` by default, and this table is stale until updated.

| Hook | Event | Group | Installs when the failure mode is… |
|---|---|---|---|
| `fable_lib.py` | (library) | core | **Always** — the others import it by name |
| `verify-ledger.py` | `PostToolUse(Write\|Edit\|Bash)` | core | **Always** — records evidence, never blocks, fail-open |
| `stop-verify-gate.py` | `Stop` | core | Claims outrun evidence (change-verification, absence-claim, claim-evidence) |
| `continuation-gate.py` | `Stop` | recommended | Work gets deferred or abandoned mid-task |
| `surfacing-gate.py` | `PreToolUse` | recommended | Risky operations run without being surfaced first |
| `blind-retry-gate.py` | `PreToolUse` | recommended | A failed command gets re-run byte-identical instead of diagnosed |
| `prompt-advance-gate.py` | `PreToolUse` | recommended | Execution starts straight after an interview/plan, with no spec pass between (Claude Code only — no Codex port yet) |
| `cutover-review-gate.py` | `Stop` | full *(opt-in)* | Cutovers/deploys get declared complete with no reviewer verdict |
| `requirements-lock.py` | `Stop` | full *(opt-in)* | Completion bias — a feature gets deleted to silence its error |
| `branch-stray-guard.sh` | `Stop` | full *(opt-in)* | Auto-committed notes land on a non-default branch and vanish |
| `skill-step-gate.py` | `Stop` | full *(opt-in)* | A skill is invoked but its required steps are skipped |
| `skill-step-inject.py` | `PostToolUse(Skill)` | full *(opt-in)* | Same as above, prevented at invoke time — pairs with `skill-step-gate` |

> `hooks/block-text-overlay.sh` ships in the directory but is **not** in any group and is not in `hooks/README.md`'s table — it is a domain-specific guard (image/text-overlay work), not part of the general bundle. Install it deliberately or not at all.

**Whatever you skip, list it.** A silent subset reads as full coverage — that is the same defect this bundle exists to catch.

**Adding a group later is normal and expected.** Start at `core`, run it for a few days, then add `recommended`. Re-running this skill for the added hooks only is correct; re-wiring hooks that already work is how a working install breaks.

## STEP 2 — Place the files where they survive

- Copy `hooks/*.py` and `hooks/*.sh` into the project's hook directory; keep `fable_lib.py` beside them (the others import it by name).
- **The evidence ledger must live outside the project tree** so it is never committed. Confirm the configured path is outside, don't assume the default.
- Make shell hooks executable. A non-executable hook fails in a way most harnesses swallow.

## STEP 3 — Wire settings atomically

- Parse the settings file, add entries, **validate the parsed result before writing**, then replace in one write. A half-written settings file can disable every hook including the ones that were working.
- Keep a copy of the pre-edit file until STEP 4 passes.

## STEP 4 — Prove each gate is live (this is the skill)

For **every** hook you wired, in this session:

1. **Positive control — make it fire.** Trigger the condition the gate exists for and confirm it blocks. Quote the block message.
2. **Negative control — make it stay quiet.** Do a normal action it should ignore and confirm nothing fires. Without this, "it blocks everything" also passes step 1.
3. **Mutation — break it and confirm it goes dark.** Remove the entry from settings (or point it at a missing file), retry the positive control, confirm the block disappears, then restore. This is what separates *"the script works"* from *"the script is wired in"*.

> **Why the mutation step is not optional.** A test that invokes the hook script directly proves the script runs. It does not prove the harness calls it. Those are different claims, and only step 3 tells them apart. Measured case (2026-08-13): a gate shipped with a self-test at 15/15 green while one of its two decision axes was **always true** — the fixtures injected that axis instead of deriving it, so the deriving code was never executed. Green count is not coverage.

4. Run the bundle's own suites: `hooks/tests/test_gate.py`, then `hooks/tests/replay/run.py` (block rate must stay 100% with the corpus floor intact) and `hooks/tests/probes/run.py`.

## STEP 5 — Report in this shape

```
Installed:   <hook> → <event> → <settings path>    [BLOCKED: "<quoted message>"]
Skipped:     <hook> — <reason>
Unverified:  <hook> — <what you could not make fire, and why>
Kill switch: FABLE_GATE_OFF=1   ·   scope to one session: FABLE_GATE_PILOT=<name>
```

**Always print the kill switch.** Someone will need to turn a gate off at a bad moment, and a gate nobody can disable gets deleted wholesale instead of scoped.

## Anti-patterns

| Thought | Reality |
|---|---|
| "Files are copied, settings updated — done." | You verified placement, not activation. STEP 4 or it is unverified. |
| "The unit tests pass." | They test the script, not the wiring. Only the mutation step covers that. |
| "It's obviously wired, the JSON is right." | JSON being right and the harness having reloaded it are two facts. Make it fire. |
| "I'll install all of them to be safe." | Unrequested gates get disabled wholesale on the first false positive. Install what fits, list what you skipped. |
| "The gate didn't fire, so nothing was wrong." | A gate that never fires and a gate that isn't wired look identical. That is what the positive control is for. |

## Turning it off

`FABLE_GATE_OFF=1` disables the gates. `FABLE_GATE_PILOT=<session-name>` scopes them to one session — use this for the first day in a shared project, then widen. Scoping detail and the per-hook switches live in [`hooks/README.md`](../../hooks/README.md).
