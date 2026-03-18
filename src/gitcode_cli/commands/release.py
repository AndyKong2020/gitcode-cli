from __future__ import annotations

import typer

from gitcode_cli.api.client import APIError
from gitcode_cli.commands.common import exit_for_api_error, json_or_render, resolve_repo_arg, root_options
from gitcode_cli.context import build_runtime
from gitcode_cli.formatting.output import print_kv, print_message, print_table


app = typer.Typer(help="Manage releases.", no_args_is_help=True)


@app.command("list")
def list_releases(
    ctx: typer.Context,
    repo: str | None = typer.Argument(None),
    limit: int = typer.Option(20, "--limit", "--per-page"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, name = resolve_repo_arg(repo, runtime)
    try:
        payload = client.request("GET", f"/api/v5/repos/{owner}/{name}/releases", params={"per_page": limit})
    except APIError as error:
        exit_for_api_error(error)
    json_or_render(json_output, payload, lambda body: print_table("Releases", ["Tag", "Name", "Created"], [[i.get("tag_name"), i.get("name"), i.get("created_at")] for i in body]))


@app.command("view")
def view_release(
    ctx: typer.Context,
    tag: str,
    repo: str | None = typer.Argument(None),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, name = resolve_repo_arg(repo, runtime)
    try:
        payload = client.request("GET", f"/api/v5/repos/{owner}/{name}/releases/{tag}")
    except APIError as error:
        exit_for_api_error(error)
    json_or_render(json_output, payload, lambda body: print_kv(f"Release {tag}", {"name": body.get("name"), "created_at": body.get("created_at"), "url": body.get("html_url"), "body": body.get("body")}))


@app.command("create")
def create_release(
    ctx: typer.Context,
    repo: str | None = typer.Argument(None),
    tag: str = typer.Option(..., "--tag"),
    name: str = typer.Option(..., "--title", "--name"),
    notes: str = typer.Option(..., "--notes", "--body"),
    target: str | None = typer.Option(None, "--target"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, repo_name = resolve_repo_arg(repo, runtime)
    try:
        payload = client.request("POST", f"/api/v5/repos/{owner}/{repo_name}/releases", json_body={"tag_name": tag, "name": name, "body": notes, "target_commitish": target})
    except APIError as error:
        exit_for_api_error(error)
    json_or_render(json_output, payload, lambda body: print_message(body.get("html_url", f"Created release {tag}")))


@app.command("delete")
def delete_release(
    ctx: typer.Context,
    tag: str,
    repo: str | None = typer.Argument(None),
    yes: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, repo_name = resolve_repo_arg(repo, runtime)
    if not yes and not typer.confirm(f"Delete release tag {tag} from {owner}/{repo_name}?", default=False):
        raise typer.Exit(code=1)
    try:
        client.request("DELETE", f"/api/v5/repos/{owner}/{repo_name}/tags/{tag}")
    except APIError as error:
        exit_for_api_error(error)
    print_message(f"Deleted tag {tag}. GitCode does not expose a dedicated release-delete endpoint, so gc deletes the backing tag.")
