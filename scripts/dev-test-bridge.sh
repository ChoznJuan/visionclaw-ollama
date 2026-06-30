#!/usr/bin/env bash
# dev-test-bridge.sh — Smoke-test the bridge with wscat.
# Phase 1 success criterion: wscat connects, gets a session.created response,
# and roundtrips a single "hello" message with audio back.

set -e

BRIDGE_URL="${BRIDGE_URL:-ws://localhost:7860/v1/realtime}"
WSCAT="${WSCAT:-wscat}"

if ! command -v "$WSCAT" >/dev/null 2>&1; then
    echo "❌ wscat not found. Install: npm install -g wscat"
    exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
    echo "❌ jq not found. Install: sudo apt install -y jq"
    exit 1
fi

echo "🔌 Connecting to $BRIDGE_URL ..."
echo ""
echo "   Send:  {\"type\": \"session.update\", \"session\": {\"voice\": \"default\"}}"
echo "   Expect: {\"type\": \"session.created\", ...}"
echo ""

# Two-step: open session, send hello, expect audio back.
# Real test will be more thorough; this is a placeholder for the spike.
exec "$WSCAT" -c "$BRIDGE_URL"
