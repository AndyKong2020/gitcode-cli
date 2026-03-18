from __future__ import annotations

import os
import subprocess
import sys

import typer

from gitcode_cli import __version__
from gitcode_cli.commands import api as api_cmd
from gitcode_cli.commands import auth, completion, config_cmd, issue, pr, release, repo, search


app = typer.Typer(help="GitCode CLI", no_args_is_help=True, pretty_exceptions_enable=False)
app.add_typer(auth.app, name="auth")
app.add_typer(repo.app, name="repo")
app.add_typer(pr.app, name="pr")
app.add_typer(issue.app, name="issue")
app.add_typer(release.app, name="release")
app.add_typer(search.app, name="search")
app.add_typer(config_cmd.app, name="config")
app.command("api")(api_cmd.api)
app.command("completion")(completion.completion)


@app.callback()
def root(
    ctx: typer.Context,
    profile: str | None = typer.Option(None, "--profile", help="Config profile to use."),
    host: str | None = typer.Option(None, "--host", help="Override the GitCode API host."),
) -> None:
    ctx.obj = {"profile": profile, "host": host}


@app.command("version")
def version() -> None:
    typer.echo(__version__)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
