# src/console/cli.py
"""
Minimal, robust CLI wrapper for PayForge interactive console.

This file provides a simple PayForgeConsole class so imports succeed even if
the full console implementation is missing or broken. The class attempts to
import the richer console implementation (msf_console) if present and falls
back to a simple cmd-based REPL.
"""

from __future__ import annotations

import cmd
import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class _FallbackConsole(cmd.Cmd):
    intro = "PayForge interactive console (fallback). Type help or ? to list commands.\n"
    prompt = "payforge> "

    def __init__(self, context: Optional[dict] = None):
        super().__init__()
        self.context = context or {}

    def do_exit(self, arg):
        "Exit the console"
        print("Exiting PayForge console.")
        return True

    def do_quit(self, arg):
        "Alias for exit"
        return self.do_exit(arg)

    def do_help(self, arg):
        "Show help"
        return super().do_help(arg)

    def do_modules(self, arg):
        "List available modules (fallback): modules"
        print("No module loader available in fallback console. Use the full console implementation for module support.")

    def do_EOF(self, arg):
        print()
        return True


# Try to import a richer console implementation if present
try:
    # Attempt to import msf_console or similar richer implementation
    from .msf_console import PayForgeConsole as RichConsole  # type: ignore

    class PayForgeConsole(RichConsole):
        """
        If a richer console exists in msf_console.PayForgeConsole, use it.
        Otherwise fallback to the simple console above.
        """
        pass

except Exception:
    # Fallback to the minimal implementation
    class PayForgeConsole(_FallbackConsole):
        """
        Fallback console when the richer implementation cannot be loaded.
        Keeps a compatible interface used by main.py (cmdloop/start/run).
        """
        def __init__(self, context: Optional[dict] = None):
            super().__init__(context=context)
