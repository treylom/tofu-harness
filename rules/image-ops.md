<!-- Full source of truth — 3-layer loading structure. This file = the complete rule text (fully preserved, nothing deleted). Always-on core summary lives in .claude/rules/image-ops.md (front-loaded).
     When a trigger matches, the rule-router hook instructs the agent to read this file. Manual edits go here (the core file holds only the summary). -->

# Rule: Image Work — Edit vs. Generate vs. Overlay

Trigger: the moment you start (or dispatch) any image generation, editing, labeling, or diagram task.

> Why (summary): On 2026-06-08, a "text-only change" (= an edit) was dispatched to a generator instead, causing full recomposition plus a PIL font-overlay tone mismatch — about 3 hours of churn (root cause: edit/generate confusion). Why #2: on 2026-07-09, a real person's face (▶ Fill in: your own reference-image example) was generated from imagination → had to be corrected twice (root cause: not following reference-first). See your incident-log entry on edit-vs-generate routing · your incident-log entry on reference-first policy. Full history: git log.
> 2026-07-31 diet edit (by the orchestrator bot): narrative compressed; decision tree, gates, and forbidden paths fully preserved.

## 1. Decision tree (what's the goal?)
- **Generating a new image** (new composition) → text-to-image (`$imagen` / gpt-image-2).
- **Editing an existing image** (composition preserved + add/modify) → **image-to-image edit** = attach the **original image + edit prompt** to `$imagen`. Composition PRESERVED.
- **Deterministic overlay** (exact pixel preservation, mechanical text, non-aesthetic technical images) → PIL/ImageMagick. ⚠️ Pasting a font over an illustration/hand-drawn image = tone mismatch ❌.

## 1.5 Type routing — diagrams, infographics, and text-heavy images: generation (GPT-image-2) is the first candidate (operator correction, 2026-08-23: "the image bot keeps misjudging what GPT-image-2 can do")
- **Diagrams, infographics, charts and graphs, posters, comics, summary cards, and images with (multilingual) text = GPT-image-2 generation is the first candidate.** The old assumption "diagrams must be built from design-system shapes, by hand, or by code rendering" is as outdated as §3's "Korean text goes on as an overlay" — do not force it in briefs or plans.
- Evidence (primary sources re-read by the orchestrator bot on 2026-08-23, plus a research bot's survey — internal notes, not shipped): ① OpenAI's announcement: "**Stronger structured generation (diagrams, infographics, charts, posters, comics) and improved multilingual text rendering**" (community.openai.com/t/introducing-gpt-image-2…/1379479) ② **#1 on the lmarena text-to-image leaderboard** (read directly on arena.ai — Arena Score 1381±5 · 70,065 votes · snapshot 2026-08-10; the score moved between 1360 and 1512 across snapshots, but **every source agreed on the #1 rank**). Priority for image benchmarks = **lmarena first, others second** (Artificial Analysis and similar = supporting labels only — the operator's call).
- **Types that require checking (not banned from generation — a person must check the output afterwards)**: ① precise **numeric** charts and graphs — no evidence found that the numbers come out accurate, so charts of real data stay code-rendered first (matplotlib and similar); use GPT-image-2 for conceptual or layout charts only ② composite assets that need a transparent background (reported as unsupported — decide after testing) ③ high-precision technical drawings and circuit diagrams (fidelity limits reported repeatedly) ④ character consistency across a multi-image series (frame drift observed). **Who records it, and where**: the bot that ordered the image runs the check **in the same turn** it collects the output (the same spot as §6 materialization verification), and appends a one-line result to the order record (the project's progress log or the order itself). Do not hand over output that has not been checked.
- Korean text = keep §3's generate-by-default rule, plus verbatim checking of the text after generation. **Korean field test, 2026-08-23 (2 images from the image bot + the orchestrator bot comparing magnified originals)**: everyday Korean (words with double final consonants, look-alike letter pairs, mixed text and numbers, a 72-character paragraph) = **rendered correctly (provisional, n=1)** / non-existent or rare syllable blocks and unfamiliar proper nouns = **silently swapped for a neighbouring syllable** (봟→밫 · 솗→솣 · 앍→앓 — 3 of 3). Because a swap does not "look broken", even a person reading the flow by eye misses it (the image bot's own first pass called everything "all correct" — a proven misjudgment). → Verbatim checking = a **letter-by-letter table** (each source syllable ↔ its crop from the render, 1:1), not OCR.
- Relation to decks and slides: deck chrome and layout stay fixed to the design system (slide-deck §2.9); **content assets** (course maps, concept diagrams, infographics, summary cards) go through this section's routing and can be proposed as generation candidates.

## 1.6 Images with Korean (Hangul) text — prompting tips (adapted from ima2-gen 3.23.1, MIT, `skills/ima2/SKILL.md`)
- Put the exact Hangul string in quotes (`"오늘의 추천"`). Don't write a vague request such as "add some Korean text".
- Describe the scene in English and keep only the visible Hangul in Korean: `A clean summer poster with the exact Korean headline "여름 축제"`. The source cites practitioner testing: all-Korean prompts produced garbled Hangul, while English prompts with a quoted Korean string rendered correctly (a heuristic, not a guarantee).
- Start with short labels (titles, buttons) and leave body-length text for last. Hangul glyphs are complex, so long, dense paragraphs break most often.
- Name the typeface (`고딕체 (Gothic/Sans-serif)` or `명조체 (Myeongjo/Serif)`), the position (top center, bottom left), and the approximate size relative to the canvas. For mixed Korean and English, say which text goes where and at what level of hierarchy.
- After generation, verify the text as described in §1.5: check each character against the requested string, and don't treat one self-check as proof that all text is correct. This section covers what to do before generation; §1.5 covers checking afterwards.

## 2. Reference-first hard gate (real people, brands, products)
- **Subjects with a "correct" appearance = reference-first, no imagination.** Secure the reference asset (path/URL/message id) first → if it exists, no text-to-image imagination-generation ❌ → do an img2img edit or reference-conditioned generation instead. The dispatch must state the reference asset path plus the identity invariants to preserve (e.g., no glasses, exact logo shape, etc.).
- No reference asset → cut over to a **generic substitute / hold / ask the operator** — do not invent a plausible-looking face or logo ❌.
- If the first result has an identity error, don't just re-prompt repeatedly ❌ → branch to img2img-with-reference / substitute / hold.

## 2.5 Text-overlay post-processing block hook (hard — 2026-07-12, adapted from ▶ Fill in: your prompt-kit vendor, MIT)
- §1's "no font-pasting ❌" is mechanically enforced by `block-text-overlay.sh` (PreToolUse:Bash) — it denies PIL ImageDraw/ImageFont, ImageMagick annotate/caption, and ffmpeg drawtext (7-fixture GREEN).
- **Legitimate escape hatch**: the §1 item-3 deterministic-overlay case passes only when explicitly declared via `ALLOW_TEXT_OVERLAY=1`. Git commands are excluded from the false-positive guard. Vendor = `▶ Fill in: your-prompt-kit-repo/` (re-sync = `git pull` on a clean tree).

## 3. Traps & signals
- "Keep the existing image as-is, just change the text / a small edit" = **an edit**. No dispatching to a generator ❌, no font-pasting ❌.
- **Worrying about "the Korean text will get mangled" during an edit = a red flag that you picked the wrong (generator) tool** (fonts/edits don't mangle text).
- `$imagen` is not banned outright ❌ — the ban applies only to "full generation with no input image." Image-input editing is a legitimate path.

## 4. Edit prompt & verification
- Prompt: "Edit this exact image. Keep frame/layout/elements 100% unchanged & inside frame. ONLY <the change>. No redraw/recompose, no spill."
- **Verification is mandatory** (don't just trust the report ❌): **pixel-diff** the original against the result (only the edited region should change; everything else should be near-identical = composition preserved, zero spill). Illustration tone = your illustration-review bot's 4-axis check / HTML = Playwright.

## 5. Dispatch ([orchestration.md §5](orchestration.md))
- The first dispatch message must fully state: edit-vs-generate + the exact method + forbidden paths (full re-generation, PIL paste, SDK, shell).
- **🚨 Image routing = your image-generation bot first (hard rule, set 2026-07-12 17:42 by the operator)**: generation/editing/asset requests → your image-generation bot (▶ Fill in: bot id, local runtime). A backup reviewer bot is the fallback only when the primary is unavailable or saturated (this supersedes an earlier "backup bot first" statement).
- **🚨 Multiple/bulk requests = vetted-prompt-kit prompts + `terra_high` sub-agent parallelism (operator standing instruction 2026-07-14 → finalized 2026-07-25, "(a) is correct")**: no sequential built-in calls ❌ → spawn `terra_high` sub-agents in parallel inside a Codex session, one `$imagegen` image per worker. Prompts = only ones that passed the vetted-prompt-kit's `check_prompt.mjs` gate.
  - **Actual mechanism (verified 2026-07-25)**: `~/.codex/config.toml` → `[features.multi_agent_v2] enabled=true`, `tool_namespace="collab_v2"` + `[agents.terra_high]` → `~/.codex/agents/terra-high.toml` (`model="gpt-5.6-terra"`, `high`). Worker isolation = a dedicated `CODEX_HOME` per worker (symlinked auth/config) → per-worker `generated_images` separation = zero collection races.
  - **⚠️ Naming correction (both axes stated — verified 2026-07-26)**: the old "`gpt-5.6-luna` sub-agent" label was **inaccurate on the sub-agent-profile axis** (the only real file under `~/.codex/agents/` is `terra-high.toml` — the accurate name is `terra_high` / `gpt-5.6-terra`). However, on the **CLI model-id axis**, `gpt-5.6-luna` is real (verified against 30 benchmark questions — a separate model) — do not correct existing benchmark labels/data that say "luna" (that would corrupt accurate data); only correct the *sub-agent dispatch path* references.
  - **❌ Forbidden path**: running ▶ Fill in: your unpinned-model direct runner script directly (spawns without pinning a model + races over the shared `generated_images` mtime claim) — use only as a fallback when sub-agents aren't available, with the reason logged in one line.
  - "Account rate limit"-style justifications for going sequential = unfounded (corrected directly by the operator on 2026-07-14). §6's materialization check is unchanged even under parallelism. Incidents: a 36-frame boss-fight sequence drifting under sequential generation · a fleet-runner run triggered by a genuine three-way source-of-truth mismatch on an asset spec (caught by the operator on 2026-07-25). 1-2 single images can still use the built-in path · the operator's call takes priority.

## 6. PPT bulk-generation output verification (2026-06-22)
- **A generation preview ≠ a delivered file.** A project-bound asset counts as delivered only after passing **file materialization verification**: record `START_TS` right before the worker starts → in `$CODEX_HOME/generated_images` and the output folder, only candidates **created after START_TS** count as candidates (otherwise report blocked — no guessing from an old file, no assuming the newest one is it, no copying from cache ❌).
- Batch verification = `file` / `sips` / `shasum`. **Identical SHA-1 across slugs = a stale-cache FAIL** — do not add it to the manifest ❌. The actual file, mtime, and hash outrank whatever the sub-agent's message claims.
- If the built-in path can't prove a fresh PNG path, or a batch of files is required, use the verified wrapper: `.claude/skills/gptimage/scripts/imagen-batch.sh <yaml> --parallel N --out-dir <dir>` (success = the original PNG's SHA-1 matches this run).
- The main agent must not just trust the sub-agent's result ❌ → re-run the same verification before merging. Manifest-append condition = row count + every path exists + correct image type + hash uniqueness.

## Applies to
- This vault's `.claude/rules/` plus bundled deliverables (ThisCode/ThisCodex). Core domain knowledge when standing up a new design bot. Conflicts: explicit user instruction > rule > default.
