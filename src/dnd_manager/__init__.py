"""D&D 5e Character Manager - CLI application for managing D&D characters."""

try:
    from importlib.metadata import version
    __version__ = version("ccvault")
except Exception:
    __version__ = "dev"
