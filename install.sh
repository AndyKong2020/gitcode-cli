#!/usr/bin/env bash
set -euo pipefail

REPO="AndyKong2020/gitcode-cli"
GC_HOME="${GC_HOME:-$HOME/.local/share/gc}"
GC_BIN_DIR="${GC_BIN_DIR:-$HOME/.local/bin}"
GC_VERSION="${GC_VERSION:-}"
INSTALL_VENV="$GC_HOME/venv"
WRAPPER_PATH="$GC_BIN_DIR/gc"
COMMAND="${1:-install}"
TMP_CLEANUP_DIR=""

log() {
  printf '%s\n' "$*"
}

fail() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "missing required command: $1"
}

latest_ref() {
  if [ -n "$GC_VERSION" ]; then
    printf '%s\n' "$GC_VERSION"
    return
  fi

  python3 - <<'PY'
import json
import urllib.request

url = "https://api.github.com/repos/AndyKong2020/gitcode-cli/releases/latest"
try:
    with urllib.request.urlopen(url, timeout=10) as response:
        payload = json.load(response)
    print(payload.get("tag_name") or "main")
except Exception:
    print("main")
PY
}

archive_url() {
  local ref="$1"
  case "$ref" in
    main)
      printf 'https://github.com/%s/archive/refs/heads/main.tar.gz\n' "$REPO"
      ;;
    *)
      printf 'https://github.com/%s/archive/refs/tags/%s.tar.gz\n' "$REPO" "$ref"
      ;;
  esac
}

warn_conflict() {
  local existing
  existing="$(command -v gc || true)"
  if [ -n "$existing" ] && [ "$existing" != "$WRAPPER_PATH" ]; then
    log "warning: another gc executable already exists at $existing"
  fi
}

install_gc() {
  need_cmd python3
  need_cmd curl
  need_cmd tar
  warn_conflict

  local ref tmp url src
  ref="$(latest_ref)"
  url="$(archive_url "$ref")"
  tmp="$(mktemp -d)"
  TMP_CLEANUP_DIR="$tmp"
  trap 'rm -rf "$TMP_CLEANUP_DIR"' EXIT

  mkdir -p "$GC_HOME" "$GC_BIN_DIR"
  curl -fsSL "$url" -o "$tmp/src.tar.gz"
  tar -xzf "$tmp/src.tar.gz" -C "$tmp"
  src="$(find "$tmp" -maxdepth 1 -type d -name 'gitcode-cli-*' | head -n 1)"
  [ -n "$src" ] || fail "failed to unpack source archive"

  python3 -m venv "$INSTALL_VENV"
  "$INSTALL_VENV/bin/python" -m pip install --upgrade pip
  "$INSTALL_VENV/bin/python" -m pip install "$src"

  cat >"$WRAPPER_PATH" <<EOF
#!/usr/bin/env bash
exec "$INSTALL_VENV/bin/gc" "\$@"
EOF
  chmod +x "$WRAPPER_PATH"

  log "Installed gc from ${ref}."
  log "Binary: $WRAPPER_PATH"
  case ":$PATH:" in
    *":$GC_BIN_DIR:"*) ;;
    *) log "Add $GC_BIN_DIR to PATH to use gc from new shells." ;;
  esac

  rm -rf "$tmp"
  TMP_CLEANUP_DIR=""
}

uninstall_gc() {
  rm -rf "$GC_HOME"
  rm -f "$WRAPPER_PATH"
  log "Removed gc."
}

case "$COMMAND" in
  install|update)
    install_gc
    ;;
  uninstall)
    uninstall_gc
    ;;
  *)
    fail "usage: install.sh [install|update|uninstall]"
    ;;
esac
