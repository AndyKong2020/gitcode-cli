from __future__ import annotations

import os
import shutil
import subprocess


SERVICE_NAME = "gc"


def _run(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _store_macos(profile: str, token: str) -> bool:
    if shutil.which("security") is None:
        return False
    result = _run(
        "security",
        "add-generic-password",
        "-a",
        profile,
        "-s",
        SERVICE_NAME,
        "-w",
        token,
        "-U",
    )
    return result.returncode == 0


def _load_macos(profile: str) -> str | None:
    if shutil.which("security") is None:
        return None
    result = _run("security", "find-generic-password", "-a", profile, "-s", SERVICE_NAME, "-w")
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _delete_macos(profile: str) -> None:
    if shutil.which("security") is None:
        return
    _run("security", "delete-generic-password", "-a", profile, "-s", SERVICE_NAME)


def _store_secret_tool(profile: str, token: str) -> bool:
    if shutil.which("secret-tool") is None:
        return False
    result = _run(
        "secret-tool",
        "store",
        "--label",
        f"gc token ({profile})",
        "service",
        SERVICE_NAME,
        "profile",
        profile,
        input_text=token,
    )
    return result.returncode == 0


def _load_secret_tool(profile: str) -> str | None:
    if shutil.which("secret-tool") is None:
        return None
    result = _run("secret-tool", "lookup", "service", SERVICE_NAME, "profile", profile)
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _delete_secret_tool(profile: str) -> None:
    if shutil.which("secret-tool") is None:
        return
    _run("secret-tool", "clear", "service", SERVICE_NAME, "profile", profile)


def store_token(profile: str, token: str, insecure_storage: bool = False) -> tuple[str, str | None]:
    if os.getenv("GITCODE_TOKEN"):
        return ("env", None)
    if sys_platform() == "darwin" and _store_macos(profile, token):
        return ("keychain", None)
    if sys_platform() == "linux" and _store_secret_tool(profile, token):
        return ("keychain", None)
    if insecure_storage:
        return ("config", token)
    return ("config", token)


def load_token(profile: str, storage: str, inline_token: str | None = None) -> str | None:
    env_token = os.getenv("GITCODE_TOKEN")
    if env_token:
        return env_token
    if storage == "keychain":
        if sys_platform() == "darwin":
            return _load_macos(profile)
        if sys_platform() == "linux":
            return _load_secret_tool(profile)
    if storage == "config":
        return inline_token
    return None


def delete_token(profile: str, storage: str) -> None:
    if storage == "keychain":
        if sys_platform() == "darwin":
            _delete_macos(profile)
        elif sys_platform() == "linux":
            _delete_secret_tool(profile)


def sys_platform() -> str:
    return os.uname().sysname.lower()
