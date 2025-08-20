"""Basic tests for Claude Shell Connector."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from claude_shell_connector import ShellConnector, ConnectorConfig
from claude_shell_connector.core.exceptions import ClaudeShellConnectorError


def test_connector_initialization():
    """Test connector can be initialized."""
    config = ConnectorConfig()
    connector = ShellConnector(config)
    
    assert connector.config == config
    assert connector.work_dir.exists()
    assert not connector.is_running()


def test_config_from_env():
    """Test configuration from environment variables."""
    with patch.dict('os.environ', {
        'CLAUDE_SHELL_WORK_DIR': '/tmp/test',
        'CLAUDE_SHELL_TIMEOUT': '60'
    }):
        config = ConnectorConfig.from_env()
        assert '/tmp/test' in config.work_dir
        assert config.default_timeout == 60.0


@pytest.mark.integration
def test_basic_command_execution():
    """Test basic command execution."""
    config = ConnectorConfig()
    
    # Skip if shell doesn't exist
    if not config.shell_path.exists():
        pytest.skip(f"Shell not found at {config.shell_path}")
    
    connector = ShellConnector(config)
    
    try:
        connector.start()
        result = connector.execute_command("echo 'test'", timeout=10)
        
        assert result.success
        assert 'test' in result.stdout
        assert result.exit_code == 0
        
    finally:
        connector.stop()


def test_import():
    """Test that main imports work."""
    from claude_shell_connector import run_command, ShellConnector
    assert run_command is not None
    assert ShellConnector is not None