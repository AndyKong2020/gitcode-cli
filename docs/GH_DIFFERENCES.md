# GitHub CLI Differences

`gc` follows the `gh` command layout, but it is not a drop-in replacement.

Current differences in v1:

- It targets GitCode APIs only
- Some GitCode resources do not have exact GitHub API equivalents
- `gc release delete` deletes the backing tag because GitCode does not expose a dedicated release delete endpoint in the bundled docs
- `gc pr review` maps to GitCode's available review endpoint rather than GitHub's review-event model
- `gc api` keeps raw REST access available when a dedicated subcommand is not implemented yet
