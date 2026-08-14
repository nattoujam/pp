#!/bin/sh
set -eu

REPO_RAW="https://raw.githubusercontent.com/nattoujam/pp/refs/heads/master/pp"
BIN_DIR="$HOME/.local/bin"

command -v curl >/dev/null 2>&1 || {
    echo "curl is required."
    exit 1
}

mkdir -p "$BIN_DIR"

tmp="$(mktemp)"
curl -fsSL "$REPO_RAW" -o "$tmp"
chmod 0755 "$tmp"
mv "$tmp" "$BIN_DIR/pp"

echo "installed: $BIN_DIR/pp"

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) echo "warning: $BIN_DIR is not in your PATH. Add it to your shell profile." ;;
esac
