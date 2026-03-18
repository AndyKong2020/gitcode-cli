from typer.testing import CliRunner
import httpx
import respx
import subprocess

from gitcode_cli.main import app


runner = CliRunner()


def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.2" in result.stdout


def test_search_docs_json():
    result = runner.invoke(app, ["search", "docs", "Create Issue", "--json"])
    assert result.exit_code == 0
    assert "Create Issue" in result.stdout


@respx.mock
def test_repo_list_json(monkeypatch):
    monkeypatch.setenv("GITCODE_TOKEN", "secret")
    respx.get("https://api.gitcode.com/api/v5/user/repos").mock(
        return_value=httpx.Response(200, json=[{"full_name": "demo/repo", "private": False, "default_branch": "main", "description": "demo"}])
    )
    result = runner.invoke(app, ["repo", "list", "--json"])
    assert result.exit_code == 0
    assert "demo/repo" in result.stdout


@respx.mock
def test_api_command(monkeypatch):
    monkeypatch.setenv("GITCODE_TOKEN", "secret")
    respx.get("https://api.gitcode.com/api/v5/user").mock(return_value=httpx.Response(200, json={"login": "me"}))
    result = runner.invoke(app, ["api", "/api/v5/user"])
    assert result.exit_code == 0
    assert '"login": "me"' in result.stdout


@respx.mock
def test_issue_create_body_file(monkeypatch, tmp_path):
    monkeypatch.setenv("GITCODE_TOKEN", "secret")
    body_file = tmp_path / "issue.md"
    body_file.write_text("from file body", encoding="utf-8")
    route = respx.post("https://api.gitcode.com/api/v5/repos/demo/issues").mock(
        return_value=httpx.Response(200, json={"number": 1, "html_url": "https://gitcode.com/demo/repo/issues/1"})
    )
    result = runner.invoke(app, ["issue", "create", "demo/repo", "--title", "From file", "--body-file", str(body_file)])
    assert result.exit_code == 0
    assert "issues/1" in result.stdout
    assert route.calls.last.request.content.decode().find("from file body") != -1


@respx.mock
def test_repo_view_web(monkeypatch):
    monkeypatch.setenv("GITCODE_TOKEN", "secret")
    respx.get("https://api.gitcode.com/api/v5/repos/demo/repo").mock(
        return_value=httpx.Response(200, json={"full_name": "demo/repo", "html_url": "https://gitcode.com/demo/repo"})
    )
    called = {}

    def fake_run(cmd, check=False):
        called["cmd"] = cmd
        return subprocess.CompletedProcess(cmd, 0)

    monkeypatch.setattr("gitcode_cli.commands.common.subprocess.run", fake_run)
    result = runner.invoke(app, ["repo", "view", "demo/repo", "--web"])
    assert result.exit_code == 0
    assert called["cmd"][-1] == "https://gitcode.com/demo/repo"
