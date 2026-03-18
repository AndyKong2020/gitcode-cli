# Authentication

`gc auth login` stores a GitCode PAT for a named profile.

Storage backend priority:

- macOS Keychain via `security`
- Linux secret service via `secret-tool`
- config file fallback

Environment override:

```bash
export GITCODE_TOKEN=...
```

This overrides stored credentials for the current shell.
