#!/usr/bin/env bash
# Block post-hoc text overlays on generated images — PreToolUse:Bash hook.
# Origin: kimsh-1/gongnyang-prompt-kit hooks/block-text-overlay.sh (MIT), adopted 2026-07-12.
# Two local adaptations: (1) legitimate deterministic-overlay cases (non-aesthetic / technical
#   images where pixel preservation matters — see [image-ops](../rules/image-ops.md) §1) pass
#   when the command declares ALLOW_TEXT_OVERLAY=1 (declarative escape instead of a blanket deny).
#   (2) git commands are exempt (commit messages mentioning ImageDraw/ImageFont are false positives).
# Text belongs INSIDE the image, rendered by the prompt. If it comes out wrong, fix the prompt
# and regenerate.
cmd=$(python3 -c 'import sys,json;print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' 2>/dev/null)
case "$cmd" in
  *ALLOW_TEXT_OVERLAY=1*) exit 0 ;;
  git\ *|rtk\ git\ *|"rtk proxy git "*) exit 0 ;;
esac
pattern='\-annotate\b|(magick|convert|mogrify)[^|;&]*(caption:|label:|pango:)|\-draw +[^|;&]{0,80}text|ImageDraw|ImageFont|drawtext'
if grep -qE "$pattern" <<<"$cmd"; then
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Post-hoc text overlay on a generated image is blocked (PIL ImageDraw / ImageMagick annotate / ffmpeg drawtext). Fix the prompt and re-render the text inside the image instead (see rules/image-ops.md section 1). For a legitimate deterministic overlay (non-aesthetic, technical image), declare intent by prefixing the command with ALLOW_TEXT_OVERLAY=1 and re-run."}}
JSON
fi
exit 0
