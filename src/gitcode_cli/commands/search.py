from __future__ import annotations

from typing import Any

import typer

from gitcode_cli.api.catalog import search_catalog
from gitcode_cli.api.client import APIError
from gitcode_cli.commands.common import exit_for_api_error, json_or_render, root_options
from gitcode_cli.context import build_runtime
from gitcode_cli.formatting.output import print_table


app = typer.Typer(help="Search repositories, issues, pull requests, and bundled API docs.", no_args_is_help=True)


def _render_repos(payload: list[dict]) -> None:
    rows = [[item.get("full_name"), item.get("stars_count"), item.get("language"), item.get("description")] for item in payload]
    print_table("Repositories", ["Name", "Stars", "Language", "Description"], rows)


def _render_issues(payload: list[dict]) -> None:
    rows = [[item.get("repository", {}).get("full_name"), item.get("number"), item.get("state"), item.get("title")] for item in payload]
    print_table("Issues", ["Repo", "Number", "State", "Title"], rows)


def _render_pulls(payload: list[dict]) -> None:
    rows = [[item.get("base", {}).get("repo", {}).get("full_name"), item.get("number"), item.get("state"), item.get("title")] for item in payload]
    print_table("Pull Requests", ["Repo", "Number", "State", "Title"], rows)


@app.command("docs")
def docs(query: str, limit: int = typer.Option(20, "--limit"), json_output: bool = typer.Option(False, "--json")) -> None:
    payload = search_catalog(query, limit=limit)
    json_or_render(
        json_output,
        payload,
        lambda items: print_table(
            "API Endpoints",
            ["Method", "Path", "Title", "Categories"],
            [[i.get("method"), i.get("path"), i.get("title"), ", ".join(i.get("categories", []))] for i in items],
        ),
    )


@app.command("repos")
def repos(
    ctx: typer.Context,
    query: str,
    owner: str | None = typer.Option(None, "--owner"),
    language: str | None = typer.Option(None, "--language"),
    limit: int = typer.Option(20, "--limit"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    try:
        payload = client.request("GET", "/api/v5/search/repositories", params={"q": query, "owner": owner, "language": language, "per_page": limit})
    except APIError as error:
        exit_for_api_error(error)
    json_or_render(json_output, payload, lambda body: _render_repos(body if isinstance(body, list) else body))


@app.command("issues")
def issues(
    ctx: typer.Context,
    query: str,
    repo: str | None = typer.Option(None, "--repo"),
    state: str | None = typer.Option(None, "--state"),
    limit: int = typer.Option(20, "--limit"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    params = {"q": query, "state": state, "per_page": limit}
    if repo and "/" in repo:
        params["repo"] = repo.split("/", 1)[1]
    try:
        payload = client.request("GET", "/api/v5/search/issues", params=params)
    except APIError as error:
        exit_for_api_error(error)
    json_or_render(json_output, payload, lambda body: _render_issues(body if isinstance(body, list) else body))


@app.command("prs")
def prs(
    ctx: typer.Context,
    query: str,
    state: str = typer.Option("open", "--state"),
    scope: str = typer.Option("created_by_me", "--scope"),
    limit: int = typer.Option(20, "--limit"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    try:
        payload = client.request("GET", "/api/v5/user/pulls", params={"state": state, "scope": scope, "per_page": limit})
    except APIError as error:
        exit_for_api_error(error)

    items = payload if isinstance(payload, list) else payload
    lowered = query.lower()
    filtered = [
        item
        for item in items
        if lowered in str(item.get("title", "")).lower() or lowered in str(item.get("body", "")).lower()
    ]
    json_or_render(json_output, filtered, _render_pulls)
