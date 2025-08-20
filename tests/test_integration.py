"""Integration tests for Claude Shell Connector."""

import os
import pytest
import time
from pathlib import Path

from claude_shell_connector import ShellConnector
from claude_shell_connector.config import ConnectorConfig
from claude_shell_connector.core.exceptions import (
    ConnectorNotRunningError,
    InvalidCommandError,
    TimeoutError,
)
from claude_shell_connector.helpers.shell import run_command, run_commands


@pytest.fixture
def temp_workspace(tmp_path):
    """Create a temporary workspace for tests."""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    
    # Create some test files
    (workspace / "test.txt").write_text("Hello, World!")
    (workspace / "test.py").write_text("print('Hello from Python!')")
    
    return workspace


@pytest.fixture
def connector():
    """Create a connector instance for testing."""
    config = ConnectorConfig()
    
    # Skip if shell doesn't exist
    if not config.shell_path.exists():
        pytest.skip(f"Shell not found at {config.shell_path}")
    
    connector = ShellConnector(config)
    yield connector
    
    # Cleanup
    if connector.is_running():
        connector.stop()


@pytest.mark.integration
class TestShellExecution:
    """Test shell command execution."""
    
    def test_basic_echo_command(self, connector):
        """Test basic echo command."""
        connector.start()
        
        result = connector.execute_command("echo 'integration test'")
        
        assert result.success
        assert "integration test" in result.stdout
        assert result.exit_code == 0
        assert result.execution_time > 0
    
    def test_command_with_working_directory(self, connector, temp_workspace):
        """Test command execution with working directory."""
        connector.start()
        
        result = connector.execute_command(
            "ls -la",
            working_dir=str(temp_workspace)
        )
        
        assert result.success
        assert "test.txt" in result.stdout
        assert "test.py" in result.stdout
    
    def test_command_timeout(self, connector):
        """Test command timeout handling."""
        connector.start()
        
        result = connector.execute_command("sleep 5", timeout=1)
        
        assert not result.success
        assert "timeout" in result.error.lower()
        assert result.exit_code == -1
    
    def test_invalid_command(self, connector):
        """Test handling of invalid commands."""
        connector.start()
        
        result = connector.execute_command("nonexistent_command_12345")
        
        assert not result.success
        assert result.exit_code != 0
        assert len(result.stderr) > 0 or result.error is not None
    
    def test_multiple_commands(self, connector):
        """Test executing multiple commands."""
        connector.start()
        
        commands = [
            "echo 'first'",
            "echo 'second'", 
            "echo 'third'"
        ]
        
        results = []
        for cmd in commands:
            result = connector.execute_command(cmd)
            results.append(result)
        
        assert len(results) == 3
        assert all(r.success for r in results)
        assert "first" in results[0].stdout
        assert "second" in results[1].stdout  
        assert "third" in results[2].stdout


@pytest.mark.integration
class TestConnectorLifecycle:
    """Test connector lifecycle management."""
    
    def test_start_stop_connector(self, connector):
        """Test starting and stopping connector."""
        assert not connector.is_running()
        
        connector.start()
        assert connector.is_running()
        
        connector.stop()
        assert not connector.is_running()
    
    def test_execute_without_start_raises_error(self, connector):
        """Test that executing without starting raises error."""
        with pytest.raises(ConnectorNotRunningError):
            connector.execute_command("echo 'test'")
    
    def test_context_manager(self):
        """Test connector as context manager."""
        config = ConnectorConfig()
        
        if not config.shell_path.exists():
            pytest.skip(f"Shell not found at {config.shell_path}")
        
        with ShellConnector(config) as connector:
            assert connector.is_running()
            
            result = connector.execute_command("echo 'context manager test'")
            assert result.success
        
        assert not connector.is_running()
    
    def test_double_start_raises_error(self, connector):
        """Test that starting twice raises error."""
        connector.start()
        
        with pytest.raises(Exception):  # Should raise ClaudeShellConnectorError
            connector.start()


@pytest.mark.integration
class TestHelperFunctions:
    """Test helper functions."""
    
    def test_run_command_helper(self):
        """Test run_command helper function."""
        result = run_command("echo 'helper test'", timeout=10)
        
        assert result.success
        assert "helper test" in result.stdout
        assert result.execution_time > 0
    
    def test_run_commands_helper(self):
        """Test run_commands helper function."""
        commands = [
            "echo 'first'",
            "echo 'second'"
        ]
        
        results = run_commands(commands, timeout=10)
        
        assert len(results) == 2
        assert all(r.success for r in results)
        assert "first" in results[0].stdout
        assert "second" in results[1].stdout
    
    def test_run_commands_stop_on_error(self):
        """Test run_commands with stop_on_error."""
        commands = [
            "echo 'before error'",
            "nonexistent_command_12345",  # This should fail
            "echo 'after error'"  # This shouldn't run
        ]
        
        results = run_commands(commands, timeout=10, stop_on_error=True)
        
        assert len(results) == 2  # Should stop after second command
        assert results[0].success
        assert not results[1].success
    
    def test_run_commands_continue_on_error(self):
        """Test run_commands with continue on error."""
        commands = [
            "echo 'before error'",
            "nonexistent_command_12345",  # This should fail
            "echo 'after error'"  # This should still run
        ]
        
        results = run_commands(commands, timeout=10, stop_on_error=False)
        
        assert len(results) == 3
        assert results[0].success
        assert not results[1].success
        assert results[2].success


@pytest.mark.integration
class TestFileOperations:
    """Test file-based operations."""
    
    def test_file_listing(self, temp_workspace):
        """Test listing files in a directory."""
        result = run_command(
            f"ls -la {temp_workspace}",
            timeout=10
        )
        
        assert result.success
        assert "test.txt" in result.stdout
        assert "test.py" in result.stdout
    
    def test_file_content_reading(self, temp_workspace):
        """Test reading file contents."""
        test_file = temp_workspace / "test.txt"
        
        result = run_command(
            f"cat {test_file}",
            timeout=10
        )
        
        assert result.success
        assert "Hello, World!" in result.stdout
    
    def test_file_creation_and_removal(self, temp_workspace):
        """Test creating and removing files."""
        test_file = temp_workspace / "created_file.txt"
        
        # Create file
        create_result = run_command(
            f"echo 'created content' > {test_file}",
            timeout=10
        )
        assert create_result.success
        
        # Verify file exists
        check_result = run_command(f"cat {test_file}", timeout=10)
        assert check_result.success
        assert "created content" in check_result.stdout
        
        # Remove file
        remove_result = run_command(f"rm {test_file}", timeout=10)
        assert remove_result.success
        
        # Verify file doesn't exist
        verify_result = run_command(
            f"cat {test_file} 2>/dev/null || echo 'file not found'",
            timeout=10
        )
        assert verify_result.success
        assert "file not found" in verify_result.stdout


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_empty_command_raises_error(self, connector):
        """Test that empty command raises error."""
        connector.start()
        
        with pytest.raises(InvalidCommandError):
            connector.execute_command("")
        
        with pytest.raises(InvalidCommandError):
            connector.execute_command("   ")  # Only whitespace
    
    def test_command_with_stderr(self, connector):
        """Test command that produces stderr."""
        connector.start()
        
        # Command that writes to stderr but succeeds
        result = connector.execute_command("echo 'error message' >&2")
        
        # Note: Some shells may handle this differently
        if not result.success:
            assert len(result.stderr) > 0 or result.error is not None
    
    def test_very_long_output(self, connector):
        """Test command with very long output."""
        connector.start()
        
        # Generate 1000 lines of output
        result = connector.execute_command(
            "for i in {1..100}; do echo 'Line $i of test output'; done",
            timeout=30
        )
        
        assert result.success
        assert result.stdout.count('\n') >= 50  # Should have many lines


@pytest.mark.integration
@pytest.mark.slow
class TestPerformance:
    """Test performance characteristics."""
    
    def test_rapid_command_execution(self, connector):
        """Test executing many commands rapidly."""
        connector.start()
        
        start_time = time.time()
        
        for i in range(10):
            result = connector.execute_command(f"echo 'Command {i}'")
            assert result.success
        
        total_time = time.time() - start_time
        
        # Should complete 10 commands in reasonable time
        assert total_time < 30  # 30 seconds should be plenty
        
        # Average time per command should be reasonable
        avg_time = total_time / 10
        assert avg_time < 3  # 3 seconds per command max
    
    def test_concurrent_execution_safety(self, connector):
        """Test that connector handles commands safely."""
        connector.start()
        
        # Execute several commands in quick succession
        commands = [f"echo 'Concurrent {i}'" for i in range(5)]
        results = []
        
        for cmd in commands:
            result = connector.execute_command(cmd)
            results.append(result)
        
        # All commands should succeed
        assert all(r.success for r in results)
        
        # Each should have unique output
        outputs = [r.stdout.strip() for r in results]
        assert len(set(outputs)) == len(outputs)  # All unique