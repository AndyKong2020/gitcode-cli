# Installation

## Supported platforms

- macOS
- Linux

Windows is not part of v1.

## Recommended paths

1. Homebrew for macOS and Linuxbrew users
2. `install.sh` everywhere else

## Install script behavior

The installer:

- detects the latest tagged release, and falls back to `main` when needed
- installs into `~/.local/share/gc`
- creates a wrapper at `~/.local/bin/gc`
- supports `install`, `update`, and `uninstall`

Environment overrides:

- `GC_HOME`
- `GC_BIN_DIR`
- `GC_VERSION`

## Upgrade strategy

- Homebrew users should use `brew upgrade gitcode-cli`
- Install script users should run `install.sh update`
