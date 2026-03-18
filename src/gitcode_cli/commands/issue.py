from __future__ import annotations

import typer

from gitcode_cli.api.client import APIError
from gitcode_cli.commands.common import exit_for_api_error, json_or_render, resolve_repo_arg, root_options
from gitcode_cli.context import build_runtime
from gitcode_cli.formatting.output import print_kv, print_message, print_table


app = typer.Typer(help="Manage issues.", no_args_is_help=True)


@app.command("list")
def list_issues(
    ctx: typer.Context,
    repo: str | None = typer.Argument(None),
    state: str = typer.Option("open", "--state"),
    limit: int = typer.Option(20, "--limit", "--per-page"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, name = resolve_repo_arg(repo, runtime)
    try:
        payload = client.request("GET", f"/api/v5/repos/{owner}/{name}/issues", params={"state": state, "per_page": limit})
    except APIError as error:
        exit_for_api_error(error)
    json_or_render(
        json_output,
        payload,
        lambda body: print_table("Issues", ["Number", "State", "Title"], [[i.get("number"), i.get("state"), i.get("title")] for i in body]),
    )


@app.command("view")
def view_issue(
    ctx: typer.Context,
    number: str,
    repo: str | None = typer.Argument(None),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, name = resolve_repo_arg(repo, runtime)
    try:
        payload = client.request("GET", f"/api/v5/repos/{owner}/{name}/issues/{number}")
    except APIError as error:
        exit_for_api_error(error)
    json_or_render(json_output, payload, lambda body: print_kv(f"Issue #{number}", {"title": body.get("title"), "state": body.get("state"), "url": body.get("html_url"), "body": body.get("body")}))


@app.command("create")
def create_issue(
    ctx: typer.Context,
    repo: str | None = typer.Argument(None),
    title: str | None = typer.Option(None, "--title"),
    body: str | None = typer.Option(None, "--body"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, name = resolve_repo_arg(repo, runtime)
    issue_title = title or typer.prompt("Issue title")
    issue_body = body if body is not None else typer.prompt("Issue body", default="")
    try:
        payload = client.request("POST", f"/api/v5/repos/{owner}/issues", json_body={"repo": name, "title": issue_title, "body": issue_body})
    except APIError as error:
        exit_for_api_error(error)
    json_or_render(json_output, payload, lambda body_obj: print_message(body_obj.get("html_url", f"#{body_obj.get('number')}")))


@app.command("edit")
def edit_issue(
    ctx: typer.Context,
    number: str,
    repo: str | None = typer.Argument(None),
    title: str | None = typer.Option(None, "--title"),
    body: str | None = typer.Option(None, "--body"),
    state: str | None = typer.Option(None, "--state"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, name = resolve_repo_arg(repo, runtime)
    payload_data = {"repo": name}
    if title is not None:
        payload_data["title"] = title
    if body is not None:
        payload_data["body"] = body
    if state is not None:
        payload_data["state"] = state
    try:
        payload = client.request("PATCH", f"/api/v5/repos/{owner}/issues/{number}", json_body=payload_data)
    except APIError as error:
        exit_for_api_error(error)
    json_or_render(json_output, payload, lambda body_obj: print_message(body_obj.get("html_url", f"Updated issue #{number}")))


@app.command("comment")
def comment_issue(
    ctx: typer.Context,
    number: str,
    repo: str | None = typer.Argument(None),
    body: str | None = typer.Option(None, "--body"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, name = resolve_repo_arg(repo, runtime)
    comment_body = body or typer.prompt("Comment")
    try:
        payload = client.request("POST", f"/api/v5/repos/{owner}/{name}/issues/{number}/comments", json_body={"body": comment_body})
    except APIError as error:
        exit_for_api_error(error)
    json_or_render(json_output, payload, lambda body_obj: print_message(f"Commented on issue #{number}"))


@app.command("close")
def close_issue(ctx: typer.Context, number: str, repo: str | None = typer.Argument(None)) -> None:
    edit_issue(ctx, number, repo=repo, state="closed", title=None, body=None, json_output=False)


@app.command("reopen")
def reopen_issue(ctx: typer.Context, number: str, repo: str | None = typer.Argument(None)) -> None:
    edit_issue(ctx, number, repo=repo, state="open", title=None, body=None, json_output=False)
