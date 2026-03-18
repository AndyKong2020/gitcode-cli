from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import typer

from gitcode_cli.api.client import GitCodeClient
from gitcode_cli.auth.credentials import delete_token, load_token, store_token
from gitcode_cli.config.store import BASE_URL, ConfigStore, ProfileConfig


@dataclass
class Runtime:
    store: ConfigStore
    profile_name: str
    profile: ProfileConfig
    host: str
    token: str | None
    cwd: Path

    def require_client(self) -> GitCodeClient:
        if not self.token:
            typer.echo("No GitCode token configured. Run `gc auth login` or set GITCODE_TOKEN.", err=True)
            raise typer.Exit(code=4)
        return GitCodeClient(base_url=self.host, token=self.token)


def build_runtime(
    profile_override: str | None = None,
    host_override: str | None = None,
    cwd: Path | None = None,
) -> Runtime:
    store = ConfigStore()
    config = store.load()
    profile_name = profile_override or config.default_profile
    profile = config.profiles.get(profile_name)
    if profile is None:
        raise typer.BadParameter(f"Unknown profile: {profile_name}")

    host = host_override or profile.host or config.defaults.get("host") or BASE_URL
    token = load_token(profile_name, profile.token_storage, profile.token)
    return Runtime(
        store=store,
        profile_name=profile_name,
        profile=profile,
        host=host,
        token=token,
        cwd=cwd or Path.cwd(),
    )


def save_profile_token(
    profile_name: str,
    token: str,
    host: str | None = None,
    insecure_storage: bool = False,
) -> str:
    store = ConfigStore()
    config = store.load()
    profile = config.profiles.get(profile_name)
    if profile is None:
        profile = ProfileConfig(name=profile_name)
        config.profiles[profile_name] = profile
    if host:
        profile.host = host
    backend, inline_token = store_token(profile_name, token, insecure_storage)
    profile.token_storage = backend
    profile.token = inline_token
    store.save(config)
    return backend


def clear_profile_token(profile_name: str) -> None:
    store = ConfigStore()
    config = store.load()
    profile = config.profiles.get(profile_name)
    if profile is None:
        return
    delete_token(profile_name, profile.token_storage)
    profile.token = None
    store.save(config)
