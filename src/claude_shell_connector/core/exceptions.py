"""Custom exceptions for Claude Shell Connector."""


class ClaudeShellConnectorError(Exception):
    """Base exception for all Claude Shell Connector errors."""
    pass


class ConnectorNotRunningError(ClaudeShellConnectorError):
    """Raised when attempting to use a connector that is not running."""
    pass


class ShellNotFoundError(ClaudeShellConnectorError):
    """Raised when the specified shell executable cannot be found."""
    pass


class InvalidCommandError(ClaudeShellConnectorError):
    """Raised when a command is invalid or malformed."""
    pass


class CommandExecutionError(ClaudeShellConnectorError):
    """Raised when command execution fails."""
    pass


class TimeoutError(ClaudeShellConnectorError):
    """Raised when a command execution times out."""
    pass


class ConfigurationError(ClaudeShellConnectorError):
    """Raised when there's an error in configuration."""
    pass


class SecurityError(ClaudeShellConnectorError):
    """Raised when a security violation is detected."""
    pass