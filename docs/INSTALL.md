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
- updates common shell startup files to unalias any existing `gc` shell alias and prepend the install bin directory to `PATH`
- supports `install`, `update`, and `uninstall`

Environment overrides:

- `GC_HOME`
- `GC_BIN_DIR`
- `GC_VERSION`

## Upgrade strategy

- Homebrew users should use `brew upgrade gitcode-cli`
- Install script users should run `install.sh update`

## First run

After install:

```bash
gc auth login
gc auth status
gc repo list
```

If your shell already had `alias gc='git commit --verbose'` or a similar shortcut, the install script now writes a managed block into common shell startup files so `gc` resolves to the CLI in new shells.

If you still need to fix it manually, add this to your shell profile:

```bash
unalias gc 2>/dev/null || true
export PATH="$HOME/.local/bin:$PATH"
```
