from __future__ import annotations

import typer
from click.shell_completion import get_completion_class
from typer.main import get_command


MODE_MAP = {
    "bash": "bash_source",
    "zsh": "zsh_source",
    "fish": "fish_source",
}


def completion(shell: str = typer.Argument(..., help="bash, zsh, or fish")) -> None:
    if shell not in MODE_MAP:
        raise typer.BadParameter("Supported shells: bash, zsh, fish")
    from gitcode_cli.main import app

    command = get_command(app)
    completion_cls = get_completion_class(shell)
    if completion_cls is None:
        raise typer.BadParameter("Shell source not supported.")
    typer.echo(completion_cls(command, {}, "gc", "_GC_COMPLETE").source())
