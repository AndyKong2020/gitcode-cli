# GitCode CLI

`gc` is a GitHub CLI-style command line interface for GitCode.

It is designed to feel familiar if you already use `gh`, while staying focused on GitCode's REST API and workflows.

## Status

v1 focuses on the core command groups:

- `gc auth`
- `gc repo`
- `gc pr`
- `gc issue`
- `gc release`
- `gc api`
- `gc search`
- `gc config`
- `gc completion`

This is not a drop-in replacement for GitHub CLI. It follows the same command-line style, but targets GitCode.

## Install

### Homebrew

```bash
brew install AndyKong2020/tap/gitcode-cli
```

### Install Script

```bash
curl -fsSL https://raw.githubusercontent.com/AndyKong2020/gitcode-cli/main/install.sh | bash
```

Update:

```bash
curl -fsSL https://raw.githubusercontent.com/AndyKong2020/gitcode-cli/main/install.sh | bash -s -- update
```

Uninstall:

```bash
curl -fsSL https://raw.githubusercontent.com/AndyKong2020/gitcode-cli/main/install.sh | bash -s -- uninstall
```

## Quick Start

Authenticate once:

```bash
gc auth login
```

Check status:

```bash
gc auth status
```

List repositories:

```bash
gc repo list
```

Inspect the current repository from a cloned GitCode repo:

```bash
gc repo view
gc pr list
gc issue list
```

Search GitCode API docs bundled with the CLI:

```bash
gc search docs "Create Issue"
```

Use the raw API escape hatch:

```bash
gc api /api/v5/user
gc api /api/v5/repos/{owner}/{repo} -P owner=my-org -P repo=my-repo
```

## Authentication

`gc` resolves the token in this order:

1. `GITCODE_TOKEN`
2. the selected profile in `~/.config/gc/config.toml`
3. a system-backed secret store

On macOS it uses Keychain via `security`.
On Linux it uses `secret-tool` when available.
If no system secret store is available, `gc auth login` can still persist the token in config.

## Configuration

Config lives at:

```text
~/.config/gc/config.toml
```

Examples:

```bash
gc config list
gc config get defaults.profile
gc config set defaults.owner AndyKong2020
gc config set profiles.work.host https://api.gitcode.com
```

## Shell Completion

```bash
gc completion zsh
gc completion bash
gc completion fish
```

## Docs

- [Install details](docs/INSTALL.md)
- [Authentication details](docs/AUTH.md)
- [gh-style behavior and differences](docs/GH_DIFFERENCES.md)
