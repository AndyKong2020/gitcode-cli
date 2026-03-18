import httpx
import respx

from gitcode_cli.api.client import APIError, GitCodeClient


@respx.mock
def test_client_sends_bearer_token():
    route = respx.get("https://api.gitcode.com/api/v5/user").mock(
        return_value=httpx.Response(200, json={"login": "tester"})
    )
    client = GitCodeClient("https://api.gitcode.com", token="secret")
    payload = client.request("GET", "/api/v5/user")
    assert payload["login"] == "tester"
    assert route.calls.last.request.headers["Authorization"] == "Bearer secret"


@respx.mock
def test_client_raises_api_error():
    respx.get("https://api.gitcode.com/api/v5/user").mock(
        return_value=httpx.Response(404, json={"message": "not found"})
    )
    client = GitCodeClient("https://api.gitcode.com", token="secret")
    try:
        client.request("GET", "/api/v5/user")
    except APIError as error:
        assert error.status_code == 404
        assert "not found" in str(error)
    else:  # pragma: no cover
        raise AssertionError("Expected APIError")
