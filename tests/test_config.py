from gitcode_cli.config.store import AppConfig, ConfigStore, ProfileConfig


def test_config_roundtrip(tmp_path):
    store = ConfigStore(tmp_path / "config.toml")
    config = AppConfig()
    config.defaults["owner"] = "AndyKong2020"
    config.profiles["work"] = ProfileConfig(name="work", host="https://example.com", token_storage="config", token="abc")
    store.save(config)

    loaded = store.load()
    assert loaded.defaults["owner"] == "AndyKong2020"
    assert loaded.profiles["work"].host == "https://example.com"
    assert loaded.profiles["work"].token == "abc"


def test_config_set_get(tmp_path):
    store = ConfigStore(tmp_path / "config.toml")
    store.load()
    store.set_value("defaults.owner", "demo")
    store.set_value("profiles.work.host", "https://alt.example.com")
    assert store.get_value("defaults.owner") == "demo"
    assert store.get_value("profiles.work.host") == "https://alt.example.com"
