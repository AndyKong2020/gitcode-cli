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
SHELL_RC_FILES="${SHELL_RC_FILES:-$HOME/.zshrc $HOME/.bashrc $HOME/.bash_profile}"
SHELL_SETUP_BEGIN="# >>> gitcode-cli >>>"
SHELL_SETUP_END="# <<< gitcode-cli <<<"

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

rewrite_shell_setup_block() {
  local file="$1"
  local tmp
  tmp="$(mktemp)"
  if [ -f "$file" ]; then
    python3 - "$file" "$tmp" "$SHELL_SETUP_BEGIN" "$SHELL_SETUP_END" <<'PY'
from pathlib import Path
import sys

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
begin = sys.argv[3]
end = sys.argv[4]

text = src.read_text(encoding="utf-8")
lines = text.splitlines()
out = []
skipping = False
for line in lines:
    stripped = line.strip()
    if stripped == begin:
        skipping = True
        continue
    if stripped == end:
        skipping = False
        continue
    if not skipping:
        out.append(line)
result = "\n".join(out).rstrip()
if result:
    result += "\n"
dst.write_text(result, encoding="utf-8")
PY
  else
    : >"$tmp"
  fi

  {
    cat "$tmp"
    printf '%s\n' "$SHELL_SETUP_BEGIN"
    printf '%s\n' 'unalias gc 2>/dev/null || true'
    printf 'export PATH="%s:$PATH"\n' "$GC_BIN_DIR"
    printf '%s\n' "$SHELL_SETUP_END"
  } >"$file"
  rm -f "$tmp"
}

ensure_shell_setup() {
  local file
  for file in $SHELL_RC_FILES; do
    rewrite_shell_setup_block "$file"
  done
  log "Updated shell startup files to unalias gc and prepend $GC_BIN_DIR to PATH."
}

remove_shell_setup() {
  local file tmp
  for file in $SHELL_RC_FILES; do
    [ -f "$file" ] || continue
    tmp="$(mktemp)"
    python3 - "$file" "$tmp" "$SHELL_SETUP_BEGIN" "$SHELL_SETUP_END" <<'PY'
from pathlib import Path
import sys

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
begin = sys.argv[3]
end = sys.argv[4]

text = src.read_text(encoding="utf-8")
lines = text.splitlines()
out = []
skipping = False
for line in lines:
    stripped = line.strip()
    if stripped == begin:
        skipping = True
        continue
    if stripped == end:
        skipping = False
        continue
    if not skipping:
        out.append(line)
result = "\n".join(out).rstrip()
if result:
    result += "\n"
dst.write_text(result, encoding="utf-8")
PY
    mv "$tmp" "$file"
  done
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
  ensure_shell_setup

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
  remove_shell_setup
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
