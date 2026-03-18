from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("gitcode-cli")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.1.1"
