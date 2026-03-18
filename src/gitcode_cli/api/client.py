from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class APIError(Exception):
    status_code: int
    message: str
    payload: Any | None = None

    def __str__(self) -> str:
        return f"{self.status_code}: {self.message}"


class GitCodeClient:
    def __init__(
        self,
        base_url: str,
        token: str | None = None,
        timeout: float = 30.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        trust_env = False
        self._client = client or httpx.Client(base_url=self.base_url, timeout=timeout, trust_env=trust_env)

    def close(self) -> None:
        self._client.close()

    def _headers(self, extra: dict[str, str] | None = None, auth_mode: str = "bearer") -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.token and auth_mode == "bearer":
            headers["Authorization"] = f"Bearer {self.token}"
        if extra:
            headers.update(extra)
        return headers

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
        auth_mode: str = "bearer",
    ) -> Any:
        request_params = dict(params or {})
        request_headers = self._headers(headers, auth_mode=auth_mode)
        if self.token and auth_mode == "query":
            request_params["access_token"] = self.token
        if self.token and auth_mode == "private-token":
            request_headers["PRIVATE-TOKEN"] = self.token
        response = self._client.request(
            method.upper(),
            path,
            params=request_params,
            json=json_body,
            data=data,
            headers=request_headers,
        )
        return self._decode_response(response)

    def _decode_response(self, response: httpx.Response) -> Any:
        content_type = response.headers.get("content-type", "")
        payload: Any
        if "application/json" in content_type:
            try:
                payload = response.json()
            except ValueError:
                payload = {"message": response.text}
        else:
            payload = {"message": response.text}

        if response.status_code >= 400:
            message = self._extract_message(payload) or response.reason_phrase
            raise APIError(response.status_code, message, payload)
        return payload

    @staticmethod
    def _extract_message(payload: Any) -> str | None:
        if isinstance(payload, dict):
            for key in ("message", "error", "error_description"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        return None
