from __future__ import annotations

import typer

from gitcode_cli.config.store import ConfigStore
from gitcode_cli.context import build_runtime, clear_profile_token, save_profile_token
from gitcode_cli.commands.common import root_options
from gitcode_cli.formatting.output import print_kv, print_message


app = typer.Typer(help="Authenticate gc with GitCode.", no_args_is_help=True)


def _profile_name(ctx: typer.Context, explicit: str | None) -> str:
    return explicit or root_options(ctx).get("profile") or ConfigStore().load().default_profile


@app.command("login")
def login(
    ctx: typer.Context,
    token: str | None = typer.Option(None, "--token", help="Personal access token."),
    profile: str | None = typer.Option(None, "--profile", help="Profile name to store."),
    host: str = typer.Option("https://api.gitcode.com", "--host", help="GitCode API host."),
    insecure_storage: bool = typer.Option(False, "--insecure-storage", help="Allow storing the token in config.toml."),
) -> None:
    profile_name = _profile_name(ctx, profile)
    token_value = token or typer.prompt("GitCode token", hide_input=True)
    backend = save_profile_token(profile_name, token_value, host=host, insecure_storage=insecure_storage)
    print_message(f"Stored credentials for profile '{profile_name}' using {backend}.")


@app.command("logout")
def logout(
    ctx: typer.Context,
    profile: str | None = typer.Option(None, "--profile", help="Profile name."),
) -> None:
    profile_name = _profile_name(ctx, profile)
    clear_profile_token(profile_name)
    print_message(f"Removed credentials for profile '{profile_name}'.")


@app.command("status")
def status(
    ctx: typer.Context,
    profile: str | None = typer.Option(None, "--profile", help="Profile name."),
) -> None:
    runtime = build_runtime(profile_override=_profile_name(ctx, profile), host_override=root_options(ctx).get("host"))
    print_kv(
        "Authentication Status",
        {
            "profile": runtime.profile_name,
            "host": runtime.host,
            "token_available": bool(runtime.token),
            "token_storage": runtime.profile.token_storage,
        },
    )


@app.command("token")
def token(
    ctx: typer.Context,
    profile: str | None = typer.Option(None, "--profile", help="Profile name."),
) -> None:
    runtime = build_runtime(profile_override=_profile_name(ctx, profile), host_override=root_options(ctx).get("host"))
    if not runtime.token:
        raise typer.Exit(code=4)
    typer.echo(runtime.token)
