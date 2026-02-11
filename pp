#!/bin/sh

VERSION="0.1.0"
REPO_RAW="https://raw.githubusercontent.com/nattoujam/pp/refs/heads/master/pp"
DEFAULT_SERVER="https://ppng.io"

CONFIG_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/nattoujam/pp/config"

# ===== load settings =====
if [ -f "$CONFIG_FILE" ]; then
    . "$CONFIG_FILE"
fi

PIPING_SERVER="${PIPING_SERVER:-$DEFAULT_SERVER}"

usage() {
    cat <<EOF
pp v$VERSION

Usage:
  Send:
    pp send CODE -f FILE
    pp s CODE -f FILE
    pp s CODE < FILE
    echo "data" | pp s CODE

  Receive:
    pp r CODE

  Other:
    pp self-update
    pp --version
    pp config set server URL
EOF
    exit 1
}

error() {
    echo "pp: $1" >&2
    exit 1
}

# ===== curl settings =====
if [ -t 2 ]; then
    CURL_PROGRESS="--progress-bar"
else
    CURL_PROGRESS="--silent"
fi

# ===== main =====
[ $# -lt 1 ] && usage

cmd="$1"
shift

case "$cmd" in
    --version)
        echo "pp $VERSION"
        exit 0
        ;;

    self-update)
    target="$(command -v pp)" || {
        echo "pp not found in PATH"
        exit 1
    }

    tmp="$(mktemp)" || exit 1

    echo "Checking for updates..."

    curl -fsSL "$REPO_RAW" -o "$tmp" || {
        echo "Download failed."
        rm -f "$tmp"
        exit 1
    }

    remote_version=$(grep '^VERSION=' "$tmp" | head -n1 | cut -d'"' -f2)
    local_version="$VERSION"

    if [ -z "$remote_version" ]; then
        echo "Could not determine remote version."
        rm -f "$tmp"
        exit 1
    fi

    if [ "$remote_version" = "$local_version" ]; then
        echo "Already up to date (v$local_version)."
        rm -f "$tmp"
        exit 0
    fi

    echo "Updating: v$local_version → v$remote_version"

    chmod +x "$tmp"

    if [ -w "$target" ]; then
        mv "$tmp" "$target"
    else
        sudo mv "$tmp" "$target"
    fi

    echo "Update complete."
    exit 0
    ;;

    config)
        sub="$1"
        key="$2"
        value="$3"

        mkdir -p "$(dirname "$CONFIG_FILE")"

        case "$sub" in
            set)
                case "$key" in
                    server)
                        echo "PIPING_SERVER=\"$value\"" > "$CONFIG_FILE"
                        echo "Server set to $value"
                        ;;
                    *)
                        error "unknown config key"
                        ;;
                esac
                ;;
            *)
                usage
                ;;
        esac
        exit 0
        ;;

    send|s)
        [ $# -lt 1 ] && usage
        code="$1"
        shift

        url="${PIPING_SERVER}/${code}"

        if [ "$1" = "-f" ]; then
            shift
            [ -z "$1" ] && error "file not specified"
            file="$1"
            [ ! -f "$file" ] && error "file not found"

            curl $CURL_PROGRESS -T "$file" "$url"
        else
            curl $CURL_PROGRESS -T - "$url"
        fi
        ;;

    r|recv|receive)
        [ $# -lt 1 ] && usage
        code="$1"

        url="${PIPING_SERVER}/${code}"

        curl $CURL_PROGRESS "$url"
        ;;

    *)
        usage
        ;;
esac
