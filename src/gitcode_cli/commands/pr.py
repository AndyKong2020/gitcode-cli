from __future__ import annotations

from pathlib import Path
import subprocess

import typer

from gitcode_cli.api.client import APIError
from gitcode_cli.commands.common import exit_for_api_error, json_or_render, open_html_url, resolve_body_input, resolve_repo_arg, root_options
from gitcode_cli.context import build_runtime
from gitcode_cli.formatting.output import print_kv, print_message, print_table
from gitcode_cli.git.repo import git_add_remote, git_checkout_pr


app = typer.Typer(help="Manage pull requests.", no_args_is_help=True)


@app.command("list")
def list_prs(
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
        payload = client.request("GET", f"/api/v5/repos/{owner}/{name}/pulls", params={"state": state, "per_page": limit, "sort": "updated"})
    except APIError as error:
        exit_for_api_error(error)
    json_or_render(
        json_output,
        payload,
        lambda body: print_table("Pull Requests", ["Number", "State", "Title", "Head", "Base"], [[i.get("number"), i.get("state"), i.get("title"), i.get("head", {}).get("ref"), i.get("base", {}).get("ref")] for i in body]),
    )


@app.command("view")
def view_pr(
    ctx: typer.Context,
    number: int,
    repo: str | None = typer.Argument(None),
    web: bool = typer.Option(False, "--web", help="Open the pull request in a browser."),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, name = resolve_repo_arg(repo, runtime)
    try:
        payload = client.request("GET", f"/api/v5/repos/{owner}/{name}/pulls/{number}")
    except APIError as error:
        exit_for_api_error(error)
    if web:
        open_html_url(payload.get("html_url", ""))
        return
    json_or_render(json_output, payload, lambda body: print_kv(f"PR #{number}", {"title": body.get("title"), "state": body.get("state"), "head": body.get("head", {}).get("ref"), "base": body.get("base", {}).get("ref"), "url": body.get("html_url"), "body": body.get("body")}))


def _current_branch() -> str | None:
    result = subprocess.run(["git", "branch", "--show-current"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


@app.command("create")
def create_pr(
    ctx: typer.Context,
    repo: str | None = typer.Argument(None),
    title: str | None = typer.Option(None, "--title"),
    body: str | None = typer.Option(None, "--body"),
    body_file: Path | None = typer.Option(None, "--body-file", exists=True, dir_okay=False, readable=True),
    base: str | None = typer.Option(None, "--base"),
    head: str | None = typer.Option(None, "--head"),
    draft: bool = typer.Option(False, "--draft"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, name = resolve_repo_arg(repo, runtime)
    repo_info = client.request("GET", f"/api/v5/repos/{owner}/{name}")
    pr_title = title or typer.prompt("Pull request title")
    pr_body = resolve_body_input(body, body_file, "Pull request body", "")
    pr_head = head or _current_branch() or typer.prompt("Head branch")
    pr_base = base or repo_info.get("default_branch") or typer.prompt("Base branch")
    try:
        payload = client.request(
            "POST",
            f"/api/v5/repos/{owner}/{name}/pulls",
            json_body={"title": pr_title, "body": pr_body, "head": pr_head, "base": pr_base, "draft": draft},
        )
    except APIError as error:
        exit_for_api_error(error)
    json_or_render(json_output, payload, lambda body_obj: print_message(body_obj.get("html_url", f"PR #{body_obj.get('number')}")))


@app.command("checkout")
def checkout_pr(
    ctx: typer.Context,
    number: int,
    repo: str | None = typer.Argument(None),
    branch: str | None = typer.Option(None, "--branch"),
    repo_path: Path = typer.Option(Path.cwd(), "--repo-path"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"), cwd=repo_path)
    client = runtime.require_client()
    owner, name = resolve_repo_arg(repo, runtime)
    try:
        payload = client.request("GET", f"/api/v5/repos/{owner}/{name}/pulls/{number}")
    except APIError as error:
        exit_for_api_error(error)
    head = payload.get("head", {}) or {}
    head_ref = head.get("ref")
    if not head_ref:
        raise typer.BadParameter("Pull request does not expose a source branch.")
    branch_name = branch or f"pr-{number}-{head_ref}"
    fork_path = payload.get("fork_path")
    remote_name = "origin"
    ref = head_ref
    if fork_path and fork_path != f"{owner}/{name}":
        remote_name = f"pr-{number}"
        git_add_remote(repo_path, remote_name, f"git@gitcode.com:{fork_path}.git")
    git_checkout_pr(repo_path, remote_name, ref, branch_name)
    print_message(f"Checked out {branch_name}")


@app.command("comment")
def comment_pr(
    ctx: typer.Context,
    number: int,
    repo: str | None = typer.Argument(None),
    body: str | None = typer.Option(None, "--body"),
    body_file: Path | None = typer.Option(None, "--body-file", exists=True, dir_okay=False, readable=True),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, name = resolve_repo_arg(repo, runtime)
    comment_body = resolve_body_input(body, body_file, "Comment")
    try:
        payload = client.request("POST", f"/api/v5/repos/{owner}/{name}/pulls/{number}/comments", json_body={"body": comment_body})
    except APIError as error:
        exit_for_api_error(error)
    json_or_render(json_output, payload, lambda body_obj: print_message(f"Commented on PR #{number}"))


@app.command("merge")
def merge_pr(
    ctx: typer.Context,
    number: int,
    repo: str | None = typer.Argument(None),
    method: str = typer.Option("merge", "--method"),
    title: str | None = typer.Option(None, "--title"),
    body: str | None = typer.Option(None, "--body"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, name = resolve_repo_arg(repo, runtime)
    try:
        payload = client.request("PUT", f"/api/v5/repos/{owner}/{name}/pulls/{number}/merge", json_body={"merge_method": method, "title": title, "description": body})
    except APIError as error:
        exit_for_api_error(error)
    json_or_render(json_output, payload, lambda body_obj: print_message(body_obj.get("message", f"Merged PR #{number}")))


@app.command("review")
def review_pr(
    ctx: typer.Context,
    number: int,
    repo: str | None = typer.Argument(None),
    force: bool = typer.Option(False, "--force"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    runtime = build_runtime(profile_override=root_options(ctx).get("profile"), host_override=root_options(ctx).get("host"))
    client = runtime.require_client()
    owner, name = resolve_repo_arg(repo, runtime)
    try:
        payload = client.request("POST", f"/api/v5/repos/{owner}/{name}/pulls/{number}/review", json_body={"force": force})
    except APIError as error:
        exit_for_api_error(error)
    json_or_render(json_output, payload, lambda _body: print_message(f"Submitted review action for PR #{number}"))
