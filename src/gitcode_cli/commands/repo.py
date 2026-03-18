from __future__ import annotations

import typer

from gitcode_cli.api.client import APIError
from gitcode_cli.commands.common import exit_for_api_error, json_or_render, open_html_url, resolve_repo_arg, root_options
from gitcode_cli.context import build_runtime
from gitcode_cli.formatting.output import print_kv, print_message, print_table
from gitcode_cli.git.repo import git_clone


app = typer.Typer(help="Manage repositories.", no_args_is_help=True)


def _repo_clone_url(payload: dict, ssh: bool) -> str:
    if ssh:
        return payload.get("ssh_url") or f"git@gitcode.com:{payload['full_name']}.git"
    return payload.get("html_url", "").rstrip("/") + ".git"


@app.command("list")
def list_repos(
    ctx: typer.Context,
    visibility: str = typer.Option("all", "--visibility"),
    page: int = typer.Option(1, "--page"),
    per_page: int = typer.Option(20, "--limit", "--per-page"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    try:
        payload = client.request("GET", "/api/v5/user/repos", params={"visibility": visibility, "page": page, "per_page": per_page})
    except APIError as error:
        exit_for_api_error(error)
    json_or_render(
        json_output,
        payload,
        lambda body: print_table(
            "Repositories",
            ["Name", "Visibility", "Branch", "Description"],
            [[item.get("full_name"), "private" if item.get("private") else "public", item.get("default_branch"), item.get("description")] for item in body],
        ),
    )


@app.command("view")
def view(
    ctx: typer.Context,
    repo: str | None = typer.Argument(None),
    web: bool = typer.Option(False, "--web", help="Open the repository in a browser."),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, name = resolve_repo_arg(repo, runtime)
    try:
        payload = client.request("GET", f"/api/v5/repos/{owner}/{name}")
    except APIError as error:
        exit_for_api_error(error)
    if web:
        open_html_url(payload.get("html_url", ""))
        return
    json_or_render(
        json_output,
        payload,
        lambda body: print_kv(
            body.get("full_name", f"{owner}/{name}"),
            {
                "description": body.get("description"),
                "default_branch": body.get("default_branch"),
                "visibility": "private" if body.get("private") else "public",
                "html_url": body.get("html_url"),
            },
        ),
    )


@app.command("create")
def create(
    ctx: typer.Context,
    name: str | None = typer.Argument(None),
    description: str = typer.Option("", "--description"),
    private: bool = typer.Option(True, "--private/--public"),
    auto_init: bool = typer.Option(True, "--auto-init/--no-auto-init"),
    clone: bool = typer.Option(False, "--clone"),
    ssh: bool = typer.Option(False, "--ssh", help="Use SSH when cloning after create."),
    default_branch: str = typer.Option("main", "--default-branch"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    repo_name = name or typer.prompt("Repository name")
    try:
        payload = client.request(
            "POST",
            "/api/v5/user/repos",
            json_body={
                "name": repo_name,
                "description": description,
                "private": private,
                "auto_init": auto_init,
                "default_branch": default_branch,
            },
        )
    except APIError as error:
        exit_for_api_error(error)
    if clone:
        git_clone(_repo_clone_url(payload, ssh=ssh))
    json_or_render(json_output, payload, lambda body: print_message(body.get("html_url", repo_name)))


@app.command("clone")
def clone(
    ctx: typer.Context,
    repo: str = typer.Argument(...),
    directory: str | None = typer.Argument(None),
    ssh: bool = typer.Option(False, "--ssh"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, name = resolve_repo_arg(repo, runtime)
    try:
        payload = client.request("GET", f"/api/v5/repos/{owner}/{name}")
    except APIError as error:
        exit_for_api_error(error)
    git_clone(_repo_clone_url(payload, ssh=ssh), directory)
    print_message(f"Cloned {owner}/{name}")


@app.command("delete")
def delete(
    ctx: typer.Context,
    repo: str | None = typer.Argument(None),
    yes: bool = typer.Option(False, "--yes", "-y"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, name = resolve_repo_arg(repo, runtime)
    if not yes and not typer.confirm(f"Delete repository {owner}/{name}?", default=False):
        raise typer.Exit(code=1)
    try:
        client.request("DELETE", f"/api/v5/repos/{owner}/{name}")
    except APIError as error:
        exit_for_api_error(error)
    print_message(f"Deleted {owner}/{name}")
