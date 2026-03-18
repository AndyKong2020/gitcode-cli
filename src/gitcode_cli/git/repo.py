from __future__ import annotations

from pathlib import Path
import re
import subprocess

import typer


REMOTE_PATTERNS = [
    re.compile(r"gitcode\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+?)(?:\.git)?$"),
    re.compile(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+?)(?:\.git)?$"),
]


def parse_repo_spec(spec: str) -> tuple[str, str]:
    if "/" not in spec:
        raise typer.BadParameter("Repository must be in OWNER/REPO format.")
    owner, repo = spec.split("/", 1)
    if not owner or not repo:
        raise typer.BadParameter("Repository must be in OWNER/REPO format.")
    return owner, repo


def infer_repo_from_git(cwd: Path | None = None) -> tuple[str, str] | None:
    path = cwd or Path.cwd()
    result = subprocess.run(
        ["git", "-C", str(path), "remote", "get-url", "origin"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    remote = result.stdout.strip()
    for pattern in REMOTE_PATTERNS:
        match = pattern.search(remote)
        if match:
            return match.group("owner"), match.group("repo")
    return None


def require_repo(spec: str | None, cwd: Path | None = None) -> tuple[str, str]:
    if spec:
        return parse_repo_spec(spec)
    inferred = infer_repo_from_git(cwd)
    if inferred:
        return inferred
    raise typer.BadParameter("Repository not specified and could not be inferred from the current git remote.")


def git_clone(url: str, directory: str | None = None) -> None:
    command = ["git", "clone", url]
    if directory:
        command.append(directory)
    raise_on_error(command)


def git_checkout_pr(repo_path: Path, remote_name: str, ref: str, branch_name: str) -> None:
    raise_on_error(["git", "-C", str(repo_path), "fetch", remote_name, ref])
    raise_on_error(["git", "-C", str(repo_path), "checkout", "-B", branch_name, "FETCH_HEAD"])


def git_add_remote(repo_path: Path, name: str, url: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo_path), "remote", "remove", name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    raise_on_error(["git", "-C", str(repo_path), "remote", "add", name, url])


def raise_on_error(command: list[str]) -> None:
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if result.returncode != 0:
        raise typer.BadParameter(result.stderr.strip() or "Git command failed.")
