#!/usr/bin/env bash
# fix_git.sh — Safely resolve stuck git states with minimal damage
#
# Default behavior:
#  1) Create a tar.gz backup in ./backups/
#  2) If a `git am`/rebase-apply session is active, abort it safely
#  3) If a rebase/merge session is active, show guidance
#  4) Show a clean status summary
#
# Options:
#   --no-backup         Skip backup tarball
#   --skip-am           If in `git am`, skip current patch instead of aborting
#   --continue-am       If in `git am`, run `git am --continue` (assumes you resolved conflicts)
#   --force-clean       Remove .git/rebase-apply and .git/rebase-merge if present (last resort)
#
# Usage:
#   scripts/fix_git.sh                # backup + abort am if present
#   scripts/fix_git.sh --skip-am      # backup + skip current am patch
#   scripts/fix_git.sh --continue-am  # continue am after manual resolution
#   scripts/fix_git.sh --no-backup    # do not create backup (faster)

set -euo pipefail

cd "$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "✖ Not inside a git repository" >&2
  exit 1
}

do_backup=1
action="abort-am"  # default action if am session detected
force_clean=0

for arg in "$@"; do
  case "$arg" in
    --no-backup) do_backup=0 ;;
    --skip-am) action="skip-am" ;;
    --continue-am) action="continue-am" ;;
    --force-clean) force_clean=1 ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done

echo "→ Repo: $(pwd)"

if [[ $do_backup -eq 1 ]]; then
  echo "→ Creating safety backup (tar.gz)"
  mkdir -p backups
  stamp=$(date +%Y%m%d-%H%M%S)
  tar_path="backups/repo-backup-$stamp.tar.gz"
  tar -czf "$tar_path" \
    --exclude=.git \
    --exclude='**/node_modules' \
    --exclude='**/__pycache__' \
    --exclude=.pytest_cache \
    --exclude=.venv \
    --exclude=backups \
    --exclude=.DS_Store \
    .
  echo "   Backup: $tar_path"
else
  echo "→ Skipping backup (per --no-backup)"
fi

echo "→ Detecting in-progress operations"

in_am=0
if git am --show-current-patch >/dev/null 2>&1; then
  in_am=1
fi
rebasing=0
if [[ -d .git/rebase-apply || -d .git/rebase-merge ]]; then
  rebasing=1
fi
merging=0
if [[ -f .git/MERGE_HEAD ]]; then
  merging=1
fi

if [[ $in_am -eq 1 ]]; then
  cur=$(git am --show-current-patch=diff 2>/dev/null | head -n 1 || true)
  echo "→ git am is in progress (${cur:-unknown patch})"
  case "$action" in
    abort-am)
      echo "   Aborting 'git am' session..."
      if git am --abort 2>/dev/null; then
        echo "   ✓ Aborted 'git am'"
      else
        echo "   ! 'git am --abort' failed; attempting manual cleanup"
        rm -rf .git/rebase-apply 2>/dev/null || true
        rm -rf .git/rebase-merge 2>/dev/null || true
      fi
      ;;
    skip-am)
      echo "   Skipping current patch..."
      git am --skip
      ;;
    continue-am)
      echo "   Attempting to continue 'git am' (ensure conflicts resolved)..."
      git add -A || true
      git am --continue
      ;;
  esac
fi

if [[ $rebasing -eq 1 ]]; then
  echo "→ A rebase is in progress (.git/rebase-apply or .git/rebase-merge present)"
  if [[ $force_clean -eq 1 ]]; then
    echo "   --force-clean set: removing rebase state dirs"
    rm -rf .git/rebase-apply .git/rebase-merge
  else
    echo "   Tip: resolve conflicts then 'git rebase --continue', or run:"
    echo "        git rebase --abort"
  fi
fi

if [[ $merging -eq 1 ]]; then
  echo "→ A merge is in progress (MERGE_HEAD present)"
  echo "   Resolve conflicts then: git add -A && git commit"
  echo "   Or abort with: git merge --abort"
fi

echo "→ Status summary"
git status -sb || git status

echo "→ Recent commits"
git log --oneline -n 5 || true

echo "✓ Done. If you still need help, run with --force-clean or share 'git status' output."

