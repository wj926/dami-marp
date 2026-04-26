#!/usr/bin/env bash
# image-gen dispatcher.
#
# Two modes:
#   1) Local (default for single-Linux setups, e.g. dami-marp upstream):
#      Set IMAGE_GEN_REMOTE='' or unset → all commands run on this machine.
#      Source-of-truth is $REMOTE_DIR (default ~/image-gen). Run `setup` once
#      to deploy chatgpt_image.py + setup_linux.sh there and create the venv.
#
#   2) Remote SSH (separated build/automation hosts, e.g. Windows + Linux):
#      Set IMAGE_GEN_REMOTE=<ssh-alias> → forwards every command over SSH,
#      with Windows↔Linux Dropbox path mapping.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REMOTE="${IMAGE_GEN_REMOTE:-}"          # empty = local mode
REMOTE_DIR="${IMAGE_GEN_DIR:-image-gen}" # relative to home

# is_local: true when running on the same machine as ChatGPT automation.
if [[ -z "$REMOTE" || "$REMOTE" == "local" ]]; then
    LOCAL=1
else
    LOCAL=0
fi

CMD="${1:-}"
shift || true

if [[ -z "$CMD" ]]; then
    echo "Usage: run.sh {setup|login|list|generate|logout} [args...]" >&2
    echo "" >&2
    echo "Mode: $([[ $LOCAL -eq 1 ]] && echo 'local (single machine)' || echo "remote SSH ($REMOTE)")" >&2
    exit 2
fi

# Map Windows Dropbox path to Linux Dropbox path (remote SSH mode only).
# Supports any local username by stripping /Users/<name>/Dropbox prefix.
map_path() {
    local p="$1"
    p="${p//\\//}"
    p="${p#[Cc]:}"
    p="${p#/[Cc]}"
    # Strip /Users/<anyname>/Dropbox or /home/<anyname>/Dropbox prefix → ~/Dropbox
    if [[ "$p" =~ ^/(Users|home)/[^/]+/Dropbox(/.*)?$ ]]; then
        p="~/Dropbox${BASH_REMATCH[2]}"
    fi
    echo "$p"
}

map_args() {
    local out=()
    for a in "$@"; do
        if (( LOCAL )); then
            # Local mode: no path remap needed
            out+=("$a")
        elif [[ "$a" == *Dropbox* || "$a" == /c/* || "$a" == C:* || "$a" == c:* ]]; then
            out+=("$(map_path "$a")")
        else
            out+=("$a")
        fi
    done
    printf '%q ' "${out[@]}"
}

# Run a command either locally or over SSH, depending on mode.
host_run() {
    if (( LOCAL )); then
        bash -c "$*"
    else
        ssh "$REMOTE" "$*"
    fi
}

# Same, but with -t (tty) for interactive sessions.
host_run_tty() {
    if (( LOCAL )); then
        bash -c "$*"
    else
        ssh -t "$REMOTE" "$*"
    fi
}

# Deploy a script to ~/$REMOTE_DIR/ on target host.
deploy_file() {
    local src="$1"
    local dst_basename="$2"
    if (( LOCAL )); then
        mkdir -p "$HOME/$REMOTE_DIR"
        cp "$src" "$HOME/$REMOTE_DIR/$dst_basename"
    else
        scp -q "$src" "$REMOTE:$REMOTE_DIR/$dst_basename"
    fi
}

case "$CMD" in
    setup)
        echo "==> Deploying scripts to ~/$REMOTE_DIR/ ($([[ $LOCAL -eq 1 ]] && echo local || echo $REMOTE))"
        if (( ! LOCAL )); then
            ssh "$REMOTE" "mkdir -p $REMOTE_DIR"
        fi
        deploy_file "$SKILL_DIR/chatgpt_image.py" "chatgpt_image.py"
        deploy_file "$SKILL_DIR/setup_linux.sh"   "setup_linux.sh"
        echo "==> Running setup..."
        host_run "bash ~/$REMOTE_DIR/setup_linux.sh"
        ;;
    login)
        deploy_file "$SKILL_DIR/chatgpt_image.py" "chatgpt_image.py"
        echo "==> Starting login session..."
        if (( ! LOCAL )); then
            echo "    1) Open a new terminal and run:  ssh -L 5900:localhost:5900 $REMOTE"
            echo "    2) Connect VNC viewer to:  localhost:5900"
            echo "    3) Log in to ChatGPT in the browser, then press Ctrl-C in THIS terminal."
            echo ""
        else
            echo "    Local mode: a Chromium window will appear on this display."
            echo "    Log in to ChatGPT, then press Ctrl-C here when done."
            echo ""
        fi
        host_run_tty "~/$REMOTE_DIR/.venv/bin/python ~/$REMOTE_DIR/chatgpt_image.py login"
        ;;
    logout)
        host_run "~/$REMOTE_DIR/.venv/bin/python ~/$REMOTE_DIR/chatgpt_image.py logout"
        ;;
    list)
        MAPPED_ARGS=$(map_args "$@")
        host_run "~/$REMOTE_DIR/.venv/bin/python ~/$REMOTE_DIR/chatgpt_image.py list $MAPPED_ARGS"
        ;;
    generate)
        deploy_file "$SKILL_DIR/chatgpt_image.py" "chatgpt_image.py"
        MAPPED_ARGS=$(map_args "$@")
        host_run_tty "~/$REMOTE_DIR/.venv/bin/python ~/$REMOTE_DIR/chatgpt_image.py generate $MAPPED_ARGS"
        ;;
    *)
        echo "Unknown command: $CMD" >&2
        echo "Usage: run.sh {setup|login|list|generate|logout} [args...]" >&2
        exit 2
        ;;
esac
