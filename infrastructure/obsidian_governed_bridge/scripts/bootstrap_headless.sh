#!/usr/bin/env bash
set -euo pipefail
cat <<'MSG'
DIGISLEUTH HEADLESS PLANE
Run this on the SEPARATE headless/agent device or environment, NOT against the same local vault path synchronized by Obsidian Desktop on your laptop.
Requires Node.js 22+ and an Obsidian Sync subscription.
MSG
npm install -g obsidian-headless
ob login
ob sync-list-remote
echo 'Next: cd into the dedicated headless vault directory, then run:'
echo '  ob sync-setup --vault "YOUR VAULT NAME"'
echo '  ob sync --continuous'
