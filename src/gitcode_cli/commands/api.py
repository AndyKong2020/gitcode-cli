from __future__ import annotations

import json
import re

import typer

from gitcode_cli.api.client import APIError, GitCodeClient
from gitcode_cli.commands.common import exit_for_api_error, root_options
from gitcode_cli.context import build_runtime
from gitcode_cli.formatting.output import print_json


def _parse_pairs(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise typer.BadParameter(f"Expected KEY=VALUE, got: {value}")
        key, item = value.split("=", 1)
        parsed[key] = item
    return parsed


def _apply_path_params(path: str, values: dict[str, str]) -> str:
    missing: list[str] = []

    def repl(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            missing.append(key)
            return match.group(0)
        return values[key]

    resolved = re.sub(r"\{([^}]+)\}", repl, path)
    if missing:
        raise typer.BadParameter(f"Missing path params: {', '.join(sorted(set(missing)))}")
    return resolved


def api(
    ctx: typer.Context,
    path: str = typer.Argument(..., help="Endpoint path, e.g. /api/v5/user"),
    method: str = typer.Option("GET", "-X", "--method"),
    field: list[str] = typer.Option([], "-F", "--field", help="JSON field KEY=VALUE"),
    query: list[str] = typer.Option([], "-Q", "--query", help="Query parameter KEY=VALUE"),
    path_param: list[str] = typer.Option([], "-P", "--path-param", help="Path parameter KEY=VALUE"),
    header: list[str] = typer.Option([], "-H", "--header", help="Header KEY=VALUE"),
    input_json: str | None = typer.Option(None, "--input-json"),
    auth_mode: str = typer.Option("bearer", "--auth-mode"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    try:
        payload = client.request(
            method,
            _apply_path_params(path, _parse_pairs(path_param)),
            params=_parse_pairs(query),
            json_body=json.loads(input_json) if input_json else (_parse_pairs(field) or None),
            headers=_parse_pairs(header),
            auth_mode=auth_mode,
        )
    except APIError as error:
        exit_for_api_error(error)
    print_json(payload)
