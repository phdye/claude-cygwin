"""
Claude Shell Connector - Bridge between Claude Desktop and shell environments.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("claude-shell-connector")
except PackageNotFoundError:
    __version__ = "1.0.0"

from .core.connector import ShellConnector
from .core.exceptions import (
    ClaudeShellConnectorError,
    CommandExecutionError,
    ConnectorNotRunningError,
    InvalidCommandError,
    ShellNotFoundError,
    TimeoutError,
)
from .helpers.shell import run_command, run_commands

__all__ = [
    "ShellConnector",
    "run_command", 
    "run_commands",
    "ClaudeShellConnectorError",
    "CommandExecutionError",
    "ConnectorNotRunningError", 
    "InvalidCommandError",
    "ShellNotFoundError",
    "TimeoutError",
    "__version__",
]