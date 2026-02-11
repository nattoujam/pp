#!/bin/sh
set -eu

REPO_RAW="https://raw.githubusercontent.com/nattoujam/pp/refs/heads/master/pp"
INSTALL_PATH="/usr/local/bin/pp"

command -v curl >/dev/null 2>&1 || {
    echo "curl is required."
    exit 1
}

tmp="$(mktemp)"

echo "Downloading pp..."
curl -fsSL "$REPO_RAW" -o "$tmp"

chmod +x "$tmp"

if [ -w "$(dirname "$INSTALL_PATH")" ]; then
    mv "$tmp" "$INSTALL_PATH"
else
    sudo mv "$tmp" "$INSTALL_PATH"
fi

echo "Installed to $INSTALL_PATH"
echo "Run: pp --version"
