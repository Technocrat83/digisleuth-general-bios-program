#!/usr/bin/env bash
set -euo pipefail
: "${OBSIDIAN_API_URL:=https://127.0.0.1:27124}"
: "${OBSIDIAN_API_KEY:?Set OBSIDIAN_API_KEY first}"
echo "[1/2] Health"
curl -ksS "$OBSIDIAN_API_URL/" | head -c 500; echo
echo "[2/2] Vault root"
curl -ksS -H "Authorization: Bearer $OBSIDIAN_API_KEY" "$OBSIDIAN_API_URL/vault/" | head -c 1000; echo
