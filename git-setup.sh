#!/bin/bash

# run bash git-setup.sh
# verify git config --list --show-origin

# ============================================================
# Git Sanity Setup Script
# Ensures predictable, safe Git behavior for student projects
# Recommended for beginners or collaborative class repos
# ============================================================

echo "Applying safe Git defaults..."

# ---- Pull behavior ----
# Merge instead of rebase when pulling (avoids rewriting history)
git config --global pull.rebase false

# ---- Push behavior ----
# Push only the current branch to its matching remote (safe default)
git config --global push.default simple

# ---- Merge behavior ----
# Disable fast-forward merges to preserve explicit merge commits
git config --global merge.ff false

# ---- Diff and log readability ----
git config --global color.ui auto
git config --global log.decorate short
git config --global core.editor "nano"   # Or "code --wait" if they use VS Code

# ---- Optional: show branch name in prompt (Linux/Mac) ----
# This line makes the terminal show the current branch automatically
git config --global bash.showBranch true

echo "Git sanity setup applied successfully!"
echo "You can verify with: git config --list --show-origin"
