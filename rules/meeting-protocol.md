<!-- Full canonical rule text. A condensed core summary can live in your bot's
     always-loaded rules file; this document is the full version your router
     should load when the meeting-protocol trigger fires. Edit this file
     directly — keep any condensed summary in sync by hand. -->

# Rule: Meeting Protocol · Bot Reliability · Timezone

Trigger: opening or progressing a meeting thread, dispatching work to a bot,
asserting a bot's status, writing a timestamp or time reference, a bot
session entering via SessionStart.

> Why (summary): an internal incident review found the same root causes
> recurring twice — an idle bot mistaken as "acknowledged = executing," a
> dispatch turn ending without verifying execution actually started, bots
> skipping the shared meeting document, and timestamp errors — leading to a
> standing instruction to bake this into both the rule files and the
> SessionStart hook. ▶ Fill in: a pointer to your own incident notes, if you
> keep them. Full provenance = your version-control history.
> Diet note: this file was trimmed once to compress narrative provenance
> while preserving every trigger, action, and cited anchor; the original
> narrative lives in your version-control log.

## 1. Shared meeting document = source of truth (raw chat ❌)

- **🚨 2+ bots collaborating or discussing = a meeting → a dedicated thread
  plus a 4-file meeting room must be created *first*** (standing hard rule,
  set 2026-06-09): do not run it in a general channel. The bot that
  convenes/chairs is responsible for creating it (if there is an
  orchestrator, orchestrator + watchdog-domain bot jointly) — assuming
  "someone else will set it up" is itself a violation. A meeting room = a
  thread + the 4 files + a watchdog, as one set. One-off announcements or
  broadcasts are not meetings → post those to your team's general channel
  instead. → [discord-comms](discord-comms.md) §3 · [orchestration](orchestration.md) §3
- **Codex-tier bots (bridge/CLI-driven workers) running long or multi-step
  dispatches should default to a meeting room (set 2026-07-16)**: automated
  watchdog coverage catches bridge delays or non-responses earlier than
  ad hoc checking would. Small one-off asks keep judgment discretion — see
  [skill-process](skill-process.md) §6.
- **🚨 Cross-check and discussion are mandatory for every meeting (standing
  hard rule, set 2026-08-01)**: do not run agenda items or prep as a flat
  split (everyone writes their own piece and stops) — instead ① assign **at
  least 2 reviewers from a different domain** to every output (each applies
  their own lens to find gaps, contradictions, or missing coverage — not
  just restate agreement), ② points of disagreement get resolved in a
  discussion round on the thread, ③ unresolved disagreement escalates to the
  operator (e.g. an interview-relay pattern). A large meeting may **split
  into sub-threads by agenda cluster as needed**, while keeping a single
  canonical 4-file record. This was the operator's direct instruction on
  2026-08-01 ("keep every meeting cross-checked across domains going
  forward," "split into separate meeting rooms when needed"). ▶ Fill in:
  your own precedent doc for a cross-check matrix format, if you keep one.
- New meeting = `<your meetings root>/<date>-<topic>/` with 4 files:
  `00-context` (immutable) / `01-spec` / `02-progress` (LIVE) / `03-outcome`.
- **`03-outcome` follow-up actions must be checkboxes (`- [ ]`)** — a prose
  action item is not picked up by an automated action collector (this
  bundle's example collector script: `self-improve-agenda.py`, requirement
  set 2026-06-10).
- **Every bot must read `02-progress` immediately before acting
  (start/complete/blocked/decision) and append
  `[<timezone> HH:MM:SS] <bot> | <state> | <one line>` immediately after.**
  Detail lives at the linked output path only — raw chat is never the
  source of truth.
  - **🚨 Second-level timestamps are mandatory, for every bot (set
    2026-06-26)**: use `HH:MM:SS` from an actual clock read (e.g.
    `date '+%H:%M:%S'`) — minute-level granularity breaks ordering for
    simultaneous appends and degrades liveness precision. Write a timestamp
    only from a fresh clock read — never from memory or assumed continuity
    (a writing-domain bot caught itself doing this on 2026-08-01).
  - **🚨 Append method and integrity contract (label: R3 — approved
    2026-08-01)**: ① Do not append with a shell `echo` that performs escape
    interpretation — it can inject real bytes (a literal `\000`/NUL byte, or
    a stray high byte such as `0xEC`) that silently vanish from grep-family
    search over the source-of-truth file, confirmed 2026-08-01 → use
    `printf '%s\n'`, your shell's raw-print form (e.g. `print -r --`), or a
    scripting-language file write instead. ② Run a NUL / valid-UTF-8 check
    once, immediately after appending. ⚠️ Do not check for a NUL byte with a
    naive `grep` empty-pattern trick — it falsely "passes" by matching every
    line instead (a writing-domain bot's positive-control test disproved it
    on 2026-08-01 at 18:02); count zero bytes directly instead (e.g. read the
    file in binary and count `0` bytes, or `tr -dc '\000' < <file> | wc -c`).
    Validate any newly introduced integrity-check command against a
    known-bad case once before relying on it.
    **①-b — 🆕 the quoting axis: even `printf`/safe-print calls can still be
    corrupted (found 2026-08-02 by a worker bot, isolated and reproduced by
    a reviewer bot, approved by the orchestrator)**: fix ① addressed *which
    command* to use but not *which quoting*. Inside **double quotes**, a
    backtick or `$` is still interpreted by the shell as command
    substitution. ⚠️ **Do not rely on shell errors or a nonzero exit code to
    catch this — the most dangerous case is the silent one**: isolated test —
    `"A \`echo XX\` B"` renders as `A XX B` with **zero stderr, exit 0**, and
    a plausible-looking but wrong value silently written to the file if the
    backtick content happens to be a valid command. If the backtick content
    is an *invalid* command, a simple (non-block) command **still** exits 0,
    because shell expansion runs before redirection — wrapping the append in
    a `{ …; } 2>...` block or a subshell does catch that half (measured:
    unwrapped invalid-command case = 0 bytes of stderr; block-wrapped
    invalid-command case = 42 bytes of stderr; a positive control such as
    `ls` on a nonexistent path = 56 bytes of stderr, confirming the `2>`
    mechanism itself works). ⚠️ **That is still only half the fix — if the
    backtick content happens to be a valid command, the block wrapper still
    produces zero stderr** (measured). The NUL/UTF-8 check in ② passes in
    every one of these cases too. ⇒ **Fix = single quotes, or a quoted
    heredoc (`<<'EOF'`) when the body itself contains a single quote, and
    verify by confirming 1-2 content anchor tokens survive immediately after
    the append** (the file "looking fine" is not evidence — anchor-token
    verification is the only check that catches both failure modes). 🆕 A
    mechanical partial fix (not yet implemented): wrapping every append in a
    `{ …; } 2>...` block catches the *invalid-command* half automatically;
    the *valid-command* half still needs the anchor-token check, so the
    wrapper does not replace it. ③ **Reporting a file's state = report SHA +
    mtime + observed-at together**, and when asserting one state came
    before/after another, **name the exact SHA being compared** — as-of
    drift between two "current" reports has been measured within windows as
    short as 10 minutes, in at least 5 documented instances; a live shared
    file's reported state is already stale by the moment you send it.
    **③-b — 🆕 that same staleness bites your own self-check (2026-08-02)**:
    reading your own just-appended line back with `tail` can hand you a line
    someone else wrote in between — measured: an 8-second gap let another
    bot's append land first, which was then misread as "my line got
    truncated," and the resulting "recovery" attempt came within one step of
    deleting the other bot's real line. ⇒ verify your own line by
    **timestamp + content anchor, never by `tail` alone**, and put an
    assertion/guard in front of any line-deleting recovery step (a filter
    built on assumptions that don't match reality is otherwise undefended —
    this guard has caught the failure mode twice in practice). Case-by-case,
    with room for re-judgment, per [skill-process](skill-process.md) §6.
    → see your own incident record for `2026-08-01-tofu-harness-followup/03-outcome.md`-style ACTION items, if you keep one.

### 1.1 Meeting folder = single canonical location (permanent, set 2026-05-19)
- **Canonical location = `<your meetings root>/<date>-<topic>/`**
  (version-controlled, so it reaches every machine on your team — symlinks
  or dotfolders are fragile across a machine boundary).
- **Banned (deprecated) locations**: any parallel/legacy meeting-notes
  folder, any symlinked copy, any dot-prefixed meeting-notes folder. Do not
  create new content in any of them.
- If this conflicts with another structural doc in your vault, this section
  wins. Migrating an existing branched folder is a destructive operation —
  get explicit sign-off first.

### 1.1.5 LATEST.md — a one-page "current state" pointer (set 2026-06-11, tracking item P1-①)
- A long-running meeting (3+ milestones, **or** `02-progress` past 30 lines)
  gets one `LATEST.md` in its folder (≤10 lines: current phase / what it's
  blocked on / one line per bot / next gate / `evidence: 02-progress
  [HH:MM] line` / update timestamp).
- **The dated canonical file never loses authority**: `02-progress` is
  append-only source of truth; `LATEST.md` is a pointer (on conflict,
  `02-progress` wins). **Update atomically (write to a temp file, then move
  it into place) and skip the rewrite entirely when content is unchanged**
  (an mtime bump with no content change is a false signal). No symlinks.
  The chairing bot updates it at each milestone; short meetings can skip it.
- **`02-progress` past 100 lines = spill (set 2026-06-12, tracking item
  P2-B)**: move detail blocks out to a numbered doc (e.g. `NN-*.md`) and
  leave `[<timezone>] <bot> | spill | → NN-doc` as the one line in
  `02-progress`. `02-progress` itself stays decisions/pointers/deadlines
  only — the standard is "you can follow the whole thread from
  `02-progress` alone."

### 1.2 Meeting roster must include the watchdog/schedule-domain bot (hard rule, set 2026-06-03)
- Every meeting's `00-context` roster **and** the watchdog's
  `--participants` list must both include your watchdog/schedule-domain bot
  (▶ Fill in: that bot's Discord user ID). Why: it owns the
  watchdog/schedule domain, so progress tracking, liveness, and recognizing
  when a meeting is done stay consistent across every meeting.
- One-off announcements/broadcasts should never spin up a new meeting → post
  to your general channel instead. A meeting = 2+ bots doing 30+ minutes of
  real work.

### 1.3 Same bot running two instances = declare an owner in `02-progress` (approved 2026-06-15)
- On opening a meeting, the first line of `02-progress` must be
  `owner=<terminal|discord> <bot> (reason)`. Any other instance of that same
  bot holds off on writing, dispatching, or triggering the completion gate
  for that meeting unless it is the declared owner.
- **Coordination between two instances of the same account has exactly one
  channel: the `02-progress` file itself** (inbound mentions to your own
  account don't reliably arrive, and peer-to-peer terminal signaling between
  instances is not allowed).
- Finding an unfamiliar entry under your own bot's name in `02-progress` is
  a signal of a dual-instance conflict → verify directly (mtime, session
  state, a live fetch — see [source-fact](source-fact.md) §3) and record the
  reconciliation. Never discard the other instance's output outright —
  archive it, verify it, then decide whether to adopt it.

## 2. Dispatch verification = a turn-ending condition (for the orchestrator)

- After dispatching work, verify **real execution entry** (e.g. via a
  terminal-session capture) at the **first checkpoint, no later than 3
  minutes** after dispatch — an acknowledgment is not the same as execution
  starting. Do not end your turn without this verification. **For a
  bridge/CLI-relayed bot: an acknowledgment turn is not an execution turn**
  → re-trigger with a self-contained "execute now" instruction if it hasn't
  actually started.

## 3. 5-10 minute active liveness daemon (watchdog + chairing orchestrator, jointly)

> **Permanent revision, set 2026-06-26: per-bot push interval = 5-10
> minutes** (the old 3-minute interval produced excessive noise; every
> legacy "3 minutes" reference within *this section* reflects this revision
> — it does not change the separate ≤3-minute dispatch-checkpoint
> requirement in §2, which answers a different question).
- During an active meeting, **push-check** each active bot every 5-10
  minutes (not a bare presence check — require a bot tag plus one line of
  actual progress). Detecting idle/silence triggers an immediate re-trigger
  mention plus a `02-progress` update.
- **Active-push duty (corrected 2026-05-21)**: each beat must send a direct
  thread mention plus a liveness probe — do not send a passive
  "waiting"-on-a-timer message. A non-responding bot gets marked idle →
  treat that as a re-trigger signal (consistent with §2).
- **🚨 Cross-check the target bot's own thread messages before pinging (set
  2026-06-26)**: fetch that bot's recent thread messages before pinging it —
  **if `02-progress` looks stale but the bot's thread activity is within
  your threshold, it is not actually silent → skip the ping** (this catches
  a false alarm produced by judging `02-progress` alone). This bundle's
  reference implementation: a `discord_recent_authors()` helper inside
  `meeting-liveness.py`, enabled by default.
- **Fetch messages in parallel to cover inbound-delivery gaps (noted
  2026-06-01)**: a bot's own message can occasionally miss the
  orchestrator's inbound feed due to timing → the daemon's push-check should
  combine a terminal-session capture with a direct thread fetch. Do not
  declare a bot idle from terminal "idle" state alone.
- **Idle judgment requires 3 axes together, plus self-line confirmation
  after an append (promoted 2026-06-15, confirmation method corrected
  2026-08-02)**: only judge idle after checking ① the `02-progress` record
  ② a token/context usage gauge increasing ③ a direct thread fetch — **all
  three, run together**. After appending to `02-progress`, confirm your own
  line survived once; if it did not, re-append (an append race is not the
  same thing as idleness — say so explicitly). ⚠️ **Confirmation method =
  locate your own line by timestamp and content anchor — not by `tail`**
  (the old "confirm with `tail`" wording is corrected here: per §1 R3 ③-b,
  on a live shared file something else can be written between your write
  and your check, so `tail` can hand you someone else's line; mistaking that
  for "my line was lost" leads to duplicate re-appends or an attempted
  delete of someone else's real line — this correction resolved a direct
  contradiction between two passages of this same document). The original
  intent — confirm survival, re-append on loss — is unchanged; only the
  confirmation method changed.
- **A 4th idle axis — distinguishing a global outage (added 2026-07-25)**:
  even when all 3 axes above say "idle," if other bots and other channels
  are *simultaneously* quiet, that is not idleness — it is an **outage**
  upstream. Diagnosis and handling: see [discord-comms](discord-comms.md) §5
  R9.
- Roster `user_id` values come from your SessionStart hook injection (§5)
  or the watchdog's manifest — never guess them.
- **🚨 "Done, waiting on something" carve-out (reviewer-bot forensic finding,
  2026-06-05)**: a bot the manifest marks `blocked_on` (waiting on the
  operator or a gate) going quiet in that meeting is normal →
  **skip the active-push probe for it** (this applies to both the automated
  daemon *and* any manual §3 push — a manual ping that ignored this
  carve-out was itself found to be false-alarm noise, per that forensic
  review). Resume probing once the block clears.
- **🚨 Per-bot `done_participants` carve-out (reviewer-bot finding,
  2026-06-07)**: when only some bots in a meeting have finished and are
  waiting, marking the *whole meeting* blocked is overkill (it also silences
  liveness checks on bots still producing output) → set
  `done_participants: <bot,..>` in the manifest to **exclude only the
  finished bots' per-bot probe** (gate-release events still reach them).
  Remove a bot from that list once it re-engages. Reference implementation:
  `done_participants()` inside `meeting-liveness.py`.
- **🚨 `blocked_on` needs a `since=` anchor, to catch a hung wait rather than
  hide it (worker-bot finding, 2026-06-06)**: any gate that could plausibly
  hide a hung bot/CLI turn must be recorded as
  `blocked_on: <gate>_<worker> (since=<ISO|HH:MM>)` — the watchdog escalates
  the carve-out to a stall once `now - since` exceeds an upper bound
  (default 20 minutes, configurable via an env var such as
  `MEETING_WATCHDOG_BLOCKED_STALL_UPPER_SEC`), and a genuinely hung turn
  should route to a human restart path (a push notification, not another
  bot mention). **Exception: an indefinite wait on a human directive can
  intentionally omit `since=`** (there is no "still progressing" assumption
  to protect, so the 20-minute upper bound would just manufacture false
  alarms — ruled by the watchdog-domain bot, 2026-06-10). Reference
  implementation: `meeting_watchdog.py`'s `_blocked_since_age`.
- **Liveness has two distinct axes — don't conflate them (set 2026-08-05,
  measured by a reviewer bot, judgment by a worker bot)**: `02-progress`
  **mtime answers "is this meeting alive"** (file-level — cheap and
  sufficient for that question). **"Did *this specific bot* do something"
  (bot-level) is a different question**, answered by something like
  `grep "] <bot> |" <02-progress-file> | tail -1` (the last timestamped line
  under that bot's name). Using the shared file's mtime to judge one bot's
  activity produces false positives — measured: two bots were both
  misjudged as "just active" off of another bot's unrelated append. State
  which question a given check actually answers (see
  [source-fact](source-fact.md) §8) — a wrong read here is usually not a
  broken check, it's a check answering a different question than the one
  being asked. ▶ Fill in: a pointer to your own planning doc, item G4, if
  you track this as an open item.

## 4. Enforce one timezone (every bot, every timestamp)

- **All timestamps in logs, notes, and scheduling decisions use one fixed
  timezone** (this bundle's example: KST / UTC+9 — ▶ Fill in: your team's
  timezone). Never expose raw UTC directly — convert first.

## 5. SessionStart hook injection contract

Your SessionStart hook should inject: (a) the active meeting's thread id +
its 4-file paths + the §1 obligations, (b) a bot-roster table of user IDs,
(c) a summary of §2 and §4. Changing the hook affects every bot → measure
and verify before editing it (see [code-quality](code-quality.md)).

## Scope

- Applies to this rule file and any copies distributed to other bots or
  machines in your fleet. Priority on conflict: explicit user instruction >
  this rule file > default behavior.
