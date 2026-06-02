#!/bin/bash
REPO_DIR="/Users/nehasinghal/Documents/aws_learning"
cd "$REPO_DIR" || exit 1
fswatch -o "$REPO_DIR" | while read -r; do
  sleep 2
  if git status --porcelain | grep -q .; then
    git add -A
    git commit -m "auto-sync $(date '+%Y-%m-%d %H:%M:%S')" --author="Neha Singhal <nehasinghal@users.noreply.github.com>" 2>/dev/null
    git push 2>/dev/null
  fi
done
