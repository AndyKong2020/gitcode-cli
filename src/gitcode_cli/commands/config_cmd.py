from __future__ import annotations

import typer

from gitcode_cli.config.store import ConfigStore
from gitcode_cli.formatting.output import print_json, print_kv


app = typer.Typer(help="Manage gc configuration.", no_args_is_help=True)


@app.command("list")
def list_config(json_output: bool = typer.Option(False, "--json", help="Print machine-readable JSON.")) -> None:
    config = ConfigStore().load().to_dict()
    if json_output:
        print_json(config)
    else:
        print_kv("Defaults", config["defaults"])
        for name, profile in config["profiles"].items():
            print_kv(f"Profile {name}", profile)


@app.command("get")
def get_value(key: str) -> None:
    value = ConfigStore().get_value(key)
    if value is None:
        raise typer.Exit(code=1)
    typer.echo(value)


@app.command("set")
def set_value(key: str, value: str) -> None:
    ConfigStore().set_value(key, value)
    typer.echo(f"Updated {key}")
