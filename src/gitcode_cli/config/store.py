from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import tomllib

from platformdirs import user_config_dir
import tomli_w

BASE_URL = "https://api.gitcode.com"


@dataclass
class ProfileConfig:
    name: str
    host: str = BASE_URL
    token_storage: str = "keychain"
    token: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = {
            "host": self.host,
            "token_storage": self.token_storage,
        }
        if self.token:
            data["token"] = self.token
        return data


@dataclass
class AppConfig:
    defaults: dict[str, Any] = field(
        default_factory=lambda: {
            "host": BASE_URL,
            "profile": "default",
            "output": "text",
            "owner": "",
        }
    )
    profiles: dict[str, ProfileConfig] = field(
        default_factory=lambda: {"default": ProfileConfig(name="default")}
    )

    @property
    def default_profile(self) -> str:
        return str(self.defaults.get("profile") or "default")

    def to_dict(self) -> dict[str, Any]:
        return {
            "defaults": self.defaults,
            "profiles": {name: profile.to_dict() for name, profile in self.profiles.items()},
        }


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        config_home = Path(user_config_dir("gc"))
        self.path = path or config_home / "config.toml"

    def load(self) -> AppConfig:
        if not self.path.exists():
            config = AppConfig()
            self.save(config)
            return config

        data = tomllib.loads(self.path.read_text(encoding="utf-8"))
        defaults = data.get("defaults", {}) or {}
        config = AppConfig(defaults={**AppConfig().defaults, **defaults}, profiles={})
        profiles = data.get("profiles", {}) or {}
        for name, raw in profiles.items():
            config.profiles[name] = ProfileConfig(
                name=name,
                host=raw.get("host", BASE_URL),
                token_storage=raw.get("token_storage", "keychain"),
                token=raw.get("token"),
            )
        if not config.profiles:
            config.profiles["default"] = ProfileConfig(name="default")
        return config

    def save(self, config: AppConfig) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(tomli_w.dumps(config.to_dict()), encoding="utf-8")

    def set_value(self, key: str, value: str) -> None:
        config = self.load()
        if key.startswith("defaults."):
            config.defaults[key.split(".", 1)[1]] = value
        elif key.startswith("profiles."):
            _, profile_name, field_name = key.split(".", 2)
            profile = config.profiles.setdefault(profile_name, ProfileConfig(name=profile_name))
            if field_name == "host":
                profile.host = value
            elif field_name == "token_storage":
                profile.token_storage = value
            elif field_name == "token":
                profile.token = value
            else:
                raise KeyError(f"Unsupported profile key: {field_name}")
        else:
            raise KeyError(f"Unsupported config key: {key}")
        self.save(config)

    def get_value(self, key: str) -> Any:
        config = self.load()
        if key.startswith("defaults."):
            return config.defaults.get(key.split(".", 1)[1])
        if key.startswith("profiles."):
            _, profile_name, field_name = key.split(".", 2)
            profile = config.profiles.get(profile_name)
            if not profile:
                return None
            return getattr(profile, field_name, None)
        raise KeyError(f"Unsupported config key: {key}")
