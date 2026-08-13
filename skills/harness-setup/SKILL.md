---
name: harness-setup
description: Use when someone wants the whole harness stood up in one pass — "set up the harness", "install everything", "한 번에 설치해줘" — including the companion plugins it works best with (conversation memory, structured brainstorming, knowledge capture). Installs in dependency order, picks a profile instead of installing everything blindly, and proves each component is live before reporting it. Also use to add one companion to an existing install, or to audit what is already wired.
---

# /harness-setup — stand the whole thing up, in order, and prove it

> Why this exists: this bundle ships gates, and the gates are the *last* thing you install. Before them there are skills, companion plugins, and an MCP server or two, each with its own failure mode — and each capable of looking installed while doing nothing. Installing them one at a time by hand means the order is wrong about half the time (a hook that imports a library that isn't there yet; a plugin whose marketplace was never added). This skill does the whole sequence, in dependency order, and **ends on proof rather than on a file listing**.

## The rule this inherits

**"Installed" means a component did its job once, in this session.** A plugin that appears in a list is *present*, not *working*. An MCP server that starts is *running*, not *answering*. This skill borrows the terminal state from [`install-hooks`](../install-hooks/SKILL.md): report success only after the thing has actually done something observable.

## STEP 0 — Census first: what is already here?

Never install over an unknown state. Before touching anything, report a table:

| Component | Present? | Live? | How you checked |
|---|---|---|---|

Check, in this order:

1. **Harness** — Claude Code (`~/.claude/settings.json`, `<project>/.claude/settings.json`) or Codex (`~/.codex/hooks.json`). Different event names; do not assume.
2. **Marketplaces already added** — list them. An already-added marketplace under a different name is the most common cause of a "duplicate plugin" mess.
3. **Plugins already installed** — and their versions.
4. **Hooks already wired** — count the entries and write the number down; you compare after.

**If a component is already present, this is an upgrade, not an install.** Say which files you are about to replace, and stop if the user has local modifications.

## STEP 1 — Pick a profile, out loud

Do not install everything by default. Name the profile you are using and what it excludes.

| Profile | Contains | Pick this when |
|---|---|---|
| **`core`** | this bundle's skills + `verify-ledger` + `stop-verify-gate` | First time here, or a shared repo where a false positive would be expensive |
| **`recommended`** | `core` + `continuation-gate` + `surfacing-gate` + conversation memory | Solo or small-team project you work in daily — **start here if unsure** |
| **`full`** | every gate in [`install-hooks`](../install-hooks/SKILL.md)'s `full` group + every companion below | You already know which gates you want and accept the tuning cost |
| **`companions-only`** | just the companion plugins, no gates | You want the tools but not the enforcement yet |

The user may also name components directly ("just add conversation memory"). That is a valid profile — record it as such.

> **Why profiles instead of "install all":** an unrequested gate that false-positives once gets the *whole bundle* disabled, not just that gate. Ship less, keep it on.

## STEP 2 — Install in dependency order

Order matters; later steps import from earlier ones.

### 2a. This bundle's skills

```
/plugin marketplace add treylom/tofu-harness
/plugin install tofu-harness@tofu-harness
```

Verify: the skills appear in the skills list. `/tofable`, `/harness-audit`, `/install-hooks`, `/harness-help` should all resolve.

### 2b. Companion plugins (skip any the profile excludes)

Install each with `/plugin marketplace add <source>` then `/plugin install <plugin>@<marketplace>`. **Add the marketplace before installing from it** — installing first fails with a message that reads like the plugin doesn't exist.

| Companion | Source | What it buys you | Verify it is live by |
|---|---|---|---|
| **conversation memory** | `jung-wan-kim/memory-bank` → `memory-bank@memory-bank-dev` | Recall across sessions — decisions and solutions from past conversations survive a context reset | Searching for something you discussed earlier and getting it back **with the right date** |
| **structured brainstorming** | `Q00/ouroboros` → `ouroboros@ouroboros` | Turns a vague idea into a decided spec via parallel adversarial review instead of one linear pass | Running one round and getting back reviewer output, not just an echo |
| **knowledge capture** | `treylom/knowledge-manager` → `km@knowledge-manager` | Captures sources (web, files, notes) into a linked knowledge base instead of a folder of orphans | Capturing one page and confirming the note has working links, not just text |

**Conversation memory needs a disk pre-flight.** It copies your conversation archive and builds an index beside it. Measured ratios on a real corpus: archive ≈ **0.77×** the source transcripts, index ≈ **0.22×**. So budget **≈ 1× the size of your transcript directory**, and require **2× free** before starting. Check first:

```bash
du -sm ~/.claude/projects | cut -f1          # source size, MB
df -k . | tail -1 | awk '{print $4/1024}'    # available, MB
```

If available < 2 × source, **stop and say so**. A half-built index is worse than none: it answers queries with a stale ceiling and gives no sign that it is truncated.

### 2c. Gates

Hand off to [`install-hooks`](../install-hooks/SKILL.md) with the profile's hook list. Do not re-implement the wiring here — that skill owns the atomic-write and mutation-test discipline.

### 2d. Rules

Copy the profile's rule files from [`rules/`](../../rules/) into the project, then **fill in the `▶ Fill in:` markers**. Count them and report the number.

> **An unfilled marker is not a weaker rule — it is an inactive one.** A completion gate whose report destination is blank never fires, and it fails silently: no error, no log line, just a gate that has never once triggered. Treat the marker count as a checklist with a number, and report how many remain.

## STEP 3 — Prove each component, then report

One proof per component. Copying files proves nothing.

| Component | Proof (must happen in this session) |
|---|---|
| Skills | Invoke one and get its behavior, not just its listing |
| Conversation memory | Retrieve a past conversation **and check the date is plausible** — a confident hit from the wrong month means the index is stale or partial |
| Brainstorming | Complete one round end to end |
| Knowledge capture | Capture one item; open the result and confirm its links resolve |
| Gates | The mutation test from `install-hooks` STEP 4 — unwire it, confirm the block disappears, restore |
| Rules | Trigger one rule's condition and observe the behavior change |

### Report shape

```
Profile:     <name>  (excluded: <what and why>)
Installed:   <component> → <version> → [PROVED: <what you observed>]
Present:     <component> — already installed, not modified
Skipped:     <component> — <reason>
Unverified:  <component> — <what you could not make happen, and why>
Markers:     <n> filled / <m> total in <rule files>
Kill switch: FABLE_GATE_OFF=1   ·   one session only: FABLE_GATE_PILOT=<name>
```

**Print the kill switch every time.** A gate nobody knows how to disable gets deleted wholesale at the first bad moment, taking the useful ones with it.

## Anti-patterns

| Thought | Reality |
|---|---|
| "Install everything, let them turn off what they don't want." | Nobody turns off one gate. They turn off all of them. Ship a profile. |
| "The plugin list shows it — done." | Present ≠ working. Every row in the STEP 3 table exists because that distinction bit someone. |
| "Conversation memory is just an index, disk is fine." | It copies the whole archive first. Measure before, not during. |
| "The rules are copied, so they apply." | Rules with unfilled markers are decoration. Count them. |
| "Setup finished without errors." | Silence is the failure mode you are guarding against. No error and no proof means unverified. |
| "I'll verify after the user starts using it." | Then the first real failure is also the first test. Prove it now, while you still know what you changed. |

## Adding one component later

This skill is re-runnable. To add a single companion to an existing install: run STEP 0 (census), name the one component as the profile, then STEP 2's row for it and STEP 3's proof. **Do not re-run the whole sequence** — re-wiring hooks that already work is how a working install becomes a broken one.
