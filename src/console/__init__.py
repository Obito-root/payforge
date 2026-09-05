# src/console/__init__.py
"""
Console package for PayForge.

Exports PayForgeConsole so `from console.cli import PayForgeConsole` works.
"""

from .cli import PayForgeConsole  # noqa: E402,F401

__all__ = ["PayForgeConsole"]
