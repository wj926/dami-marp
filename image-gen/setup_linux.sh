#!/usr/bin/env bash
# Installer for image-gen sub-skill on remote Linux host (Ubuntu 24.04).
# Idempotent: safe to re-run.
set -euo pipefail

ROOT="$HOME/image-gen"
VENV="$ROOT/.venv"

echo "==> Ensuring system packages (Xvfb, x11vnc, python venv)..."
if ! command -v Xvfb >/dev/null; then
    sudo apt-get update
    sudo apt-get install -y xvfb
fi
if ! command -v x11vnc >/dev/null; then
    sudo apt-get install -y x11vnc
fi
if ! dpkg -s python3-venv >/dev/null 2>&1; then
    sudo apt-get install -y python3-venv
fi

echo "==> Creating Python venv at $VENV..."
if [[ ! -d "$VENV" ]]; then
    python3 -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"

echo "==> Installing Python deps..."
pip install --upgrade pip >/dev/null
pip install --quiet playwright

echo "==> Installing Playwright Chromium binary (no system deps — Google Chrome libs reused)..."
"$VENV/bin/playwright" install chromium

mkdir -p "$HOME/.cache/chatgpt-image-profile"

echo ""
echo "✅ Setup complete."
echo "   Script:   $ROOT/chatgpt_image.py"
echo "   Venv:     $VENV"
echo "   Profile:  \$HOME/.cache/chatgpt-image-profile/"
echo ""
echo "Next steps:"
echo "  1) bash ~/.claude/skills/dami-marp/image-gen/run.sh login"
echo "  2) Follow VNC instructions to log into ChatGPT"
