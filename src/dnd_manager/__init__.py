"""D&D 5e Character Manager - CLI application for managing D&D characters."""

try:
    from importlib.metadata import version, PackageNotFoundError
    __version__ = version("ccvault")
except PackageNotFoundError:
    __version__ = "dev"
