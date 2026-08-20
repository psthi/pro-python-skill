#!/usr/bin/env bash
# ==============================================================================
# Pro Python Universal Skill Installer
# Links or installs this skill package into all local agent environments.
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "📦 Installing Pro Python Skill from: ${SCRIPT_DIR}"

TARGET_DIRS=(
  "$HOME/.agents/skills/pro-python"
  "$HOME/.agents/skills/python"
  "$HOME/.gemini/config/skills/pro-python"
  "$HOME/.claude/skills/pro-python"
  "$HOME/.codex/skills/pro-python"
  "$HOME/.nanobot/workspace/skills/pro-python"
  "$HOME/.picoclaw/workspace/skills/pro-python"
  "$HOME/.hermes/skills/python"
  "$HOME/skills/pro-python"
)

SUCCESS_COUNT=0

for TARGET in "${TARGET_DIRS[@]}"; do
  PARENT_DIR="$(dirname "$TARGET")"
  if [ -d "$PARENT_DIR" ]; then
    mkdir -p "$PARENT_DIR"
    rm -rf "$TARGET"
    if [[ "$TARGET" == *"picoclaw"* ]]; then
      cp -r "$SCRIPT_DIR" "$TARGET"
      echo "  ✅ Copied into PicoClaw: $TARGET"
    else
      ln -s "$SCRIPT_DIR" "$TARGET" 2>/dev/null || cp -r "$SCRIPT_DIR" "$TARGET"
      echo "  ✅ Linked into: $TARGET"
    fi
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
  fi
done

echo ""
echo "🎉 Successfully installed Pro Python Skill across ${SUCCESS_COUNT} local agent environments!"
