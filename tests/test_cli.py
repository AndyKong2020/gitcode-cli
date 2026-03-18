from typer.testing import CliRunner
import httpx
import respx

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
