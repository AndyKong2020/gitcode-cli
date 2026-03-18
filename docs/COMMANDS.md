# Command Examples

## Authentication

```bash
gc auth login
gc auth status
gc auth token
gc auth logout
```

## Repositories

```bash
gc repo list
gc repo list --json
gc repo view my-org/my-repo
gc repo view --web
gc repo create demo-repo --public --clone
gc repo create demo-repo --clone --ssh
gc repo clone my-org/my-repo
gc repo delete my-org/my-repo --yes
```

## Pull Requests

```bash
gc pr list
gc pr list my-org/my-repo --state closed
gc pr view 12
gc pr view 12 --web
gc pr create my-org/my-repo --title "Improve logs" --body-file ./pr.md --base main --head feature/logs
gc pr checkout 12
gc pr comment 12 --body-file ./comment.md
gc pr merge 12 --method squash
gc pr review 12
```

## Issues

```bash
gc issue list
gc issue view 34
gc issue view 34 --web
gc issue create my-org/my-repo --title "Crash on launch" --body-file ./issue.md
gc issue edit 34 --body-file ./updated-issue.md
gc issue comment 34 --body "Looking into this now."
gc issue close 34
gc issue reopen 34
```

## Releases

```bash
gc release list
gc release view v1.2.3
gc release view v1.2.3 --web
gc release create my-org/my-repo --tag v1.2.3 --title "v1.2.3" --notes-file ./release-notes.md
gc release delete v1.2.3 --yes
```

## Search and Raw API

```bash
gc search docs "Create Issue"
gc search repos review pilot
gc api /api/v5/user
gc api /api/v5/repos/{owner}/{repo} -P owner=my-org -P repo=my-repo
```

## Completion

```bash
gc completion zsh > "${fpath[1]}/_gc"
gc completion bash > ~/.local/share/bash-completion/completions/gc
gc completion fish > ~/.config/fish/completions/gc.fish
```
