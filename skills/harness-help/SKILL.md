---
name: harness-help
description: Use when someone asks what this harness offers, what is already installed, what a particular skill or gate does, or where to start — "what can this do", "harness help", "뭐가 설치돼 있어?", "어떻게 시작해?". Reports the live install state measured from the machine, not a static feature list, and names the one next step that fits what is missing.
---

# /harness-help — what this is, what you have, what to do next

> Why this exists: a feature list tells you what *exists*; it does not tell you what is *running here*. Those diverge fast — a gate whose settings entry was never reloaded, a skill installed under a different marketplace, a rule file copied but never filled in. This command answers from the machine, then points at exactly one next step.

## The rule

**Report measured state, never a remembered feature list.** Every "installed ✓" in your output must come from something you checked in this session. If you could not check something, print `?` and say why — a confident wrong inventory is worse than an honest gap, because the user stops looking.

## STEP 1 — Measure

Check and record, quietly, before printing anything:

1. **Harness** — Claude Code (`~/.claude/settings.json`, `<project>/.claude/settings.json`) or Codex (`~/.codex/hooks.json`).
2. **Skills** — which of this bundle's skills resolve.
3. **Gates** — parse the settings file(s) and list which hooks are wired, to which events. **Read both the user-level and project-level file**; hooks merge across them, and a hook present in one is easy to miss when you only read the other.
4. **Companions** — conversation memory, structured brainstorming, knowledge capture: installed? responding?
5. **Rules** — which rule files are present, and how many `▶ Fill in:` markers remain unfilled:
   ```bash
   grep -o '▶ Fill in' rules/*.md | wc -l
   ```
   Use `grep -o … | wc -l`, not `grep -c` — `grep -c` counts *lines*, so a line carrying two markers is undercounted.

## STEP 2 — Print this

```
HARNESS: <Claude Code | Codex>          settings: <paths actually read>

SKILLS
  /tofable         run a task under the working discipline      [installed ✓ | missing]
  /harness-audit   check harness docs for drift after a model release
  /harness-setup   stand the whole stack up in one pass
  /install-hooks   wire the gates and prove each one fires
  /harness-help    this

GATES        <n> wired  ·  group: <core | recommended | full | mixed>
  <hook> → <event>                                   [live | wired-but-unproven]
  not wired: <list>

COMPANIONS
  conversation memory   [installed ✓ · last indexed <date> | missing]
  structured brainstorm  [installed ✓ | missing]
  knowledge capture      [installed ✓ | missing]

RULES        <n> files  ·  <m> markers still unfilled   ← these rules are inactive until filled

NEXT: <exactly one step>
```

## STEP 3 — Pick the one next step

Print **one**, chosen by the first row that matches:

| If | Next step |
|---|---|
| Nothing installed | `/harness-setup` with the `recommended` profile |
| Skills present, no gates | `/install-hooks` with the `core` group |
| Gates wired but never observed firing | Prove one: `/install-hooks` STEP 4 (positive control + mutation) |
| Markers unfilled | Fill them — name the file with the most |
| `core` running clean for a while | Add the `recommended` group |
| Everything wired and proven | Nothing. Say so plainly. |

Do not print a list of five things. A single next step gets done; a menu gets postponed.

## What each piece buys you

Say this in plain language when asked "what does X do" — lead with the failure it prevents, not the mechanism.

| Piece | The failure it prevents | What you'll notice |
|---|---|---|
| `verify-ledger` | Claims made with no evidence behind them | Nothing, until another gate needs the record — it never blocks |
| `stop-verify-gate` | "Done / fixed / verified" with nothing run | You get asked for the command output before the turn ends |
| `continuation-gate` | Work quietly abandoned mid-task | Deferring something makes you name the blocker and whose call it is |
| `surfacing-gate` | Risky operations running unannounced | Destructive commands get surfaced before they run, not after |
| `blind-retry-gate` | The same failed command re-run unchanged | One bounce asking for a cause or a probe; an intentional retry costs one bounce |
| `prompt-advance-gate` | Building straight after an interview, with no spec in between | One bounce to turn the requirement into an actual spec |
| conversation memory | Losing decisions to a context reset | Past conversations become searchable — **check the dates on what comes back** |
| structured brainstorming | A vague idea going straight to code | Adversarial review before commitment, not after |
| knowledge capture | Captured pages becoming orphans | Notes arrive linked into what you already have |
| `rules/` | Yesterday's discipline silently expiring | Behavior changes at the trigger, not from a reminder |

**Be honest about the size of the effect.** The measured benchmark numbers in [`bench/results.md`](../../bench/results.md) come from an earlier model generation; a stronger model needs fewer of these corrections. The direction holds, the magnitude shrinks. Do not quote those figures as what the user should expect on their own setup.

## Turning things off

`FABLE_GATE_OFF=1` disables the gates. `FABLE_GATE_PILOT=<session-name>` scopes them to one session — use it for the first day in a shared project, then widen. Per-hook switches: [`hooks/README.md`](../../hooks/README.md).

**Always print the kill switch when asked for help.** Someone reading help is often reading it because something is in their way.

## Anti-patterns

| Thought | Reality |
|---|---|
| "I'll list the features from the README." | Then you are describing the repo, not their machine. Measure first. |
| "It's in `settings.json`, so it's live." | Wired and firing are different claims. Mark unproven ones `wired-but-unproven`. |
| "I'll give them all the next steps." | A menu gets postponed. Pick one. |
| "The rule files are copied, so the rules apply." | Unfilled markers = inactive. Count them and say the number. |
| "I only read the project settings." | Hooks merge from user-level too. Reading one file and reporting a total is how a present hook gets reported missing. |
