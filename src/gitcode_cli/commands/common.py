from __future__ import annotations

from typing import Any

import typer

from gitcode_cli.api.client import APIError
from gitcode_cli.context import Runtime
from gitcode_cli.formatting.output import print_json, print_message
from gitcode_cli.git.repo import require_repo


def root_options(ctx: typer.Context) -> dict:
    root = ctx.find_root()
    return root.obj or {}


def exit_for_api_error(error: APIError) -> None:
    print_message(f"[red]GitCode API error:[/red] {error}")
    raise typer.Exit(code=error.status_code if error.status_code < 256 else 1)


def json_or_render(json_output: bool, payload: Any, render_fn) -> None:
    if json_output:
        print_json(payload)
    else:
        render_fn(payload)


def resolve_repo_arg(repo: str | None, runtime: Runtime) -> tuple[str, str]:
    return require_repo(repo, runtime.cwd)
