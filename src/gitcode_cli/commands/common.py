from __future__ import annotations

from pathlib import Path
import subprocess
import sys
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


def resolve_body_input(body: str | None, body_file: Path | None, prompt_label: str, prompt_default: str = "") -> str:
    if body is not None and body_file is not None:
        raise typer.BadParameter("Use either --body or --body-file, not both.")
    if body_file is not None:
        return body_file.read_text(encoding="utf-8")
    if body is not None:
        return body
    return typer.prompt(prompt_label, default=prompt_default)


def open_html_url(url: str) -> None:
    if not url:
        raise typer.BadParameter("No HTML URL is available for this resource.")
    if sys.platform == "darwin":
        subprocess.run(["open", url], check=False)
        return
    if sys.platform.startswith("linux"):
        subprocess.run(["xdg-open", url], check=False)
        return
    print_message(url)
