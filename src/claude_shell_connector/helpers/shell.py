"""Helper functions for Claude Shell Connector."""

import json
import time
import uuid
from pathlib import Path
from typing import List, Optional

from ..config.settings import ConnectorConfig
from ..core.connector import CommandResult, ShellConnector


def run_command(
    command: str,
    working_dir: Optional[str] = None,
    timeout: float = 30,
    work_dir: Optional[str] = None,
) -> CommandResult:
    """
    Run a single command using the shell connector.
    
    Args:
        command: Shell command to execute
        working_dir: Working directory for command execution
        timeout: Maximum execution time in seconds
        work_dir: Communication directory (defaults to ./claude_connector)
    
    Returns:
        CommandResult: Result of command execution
    """
    # Check if connector is running by looking for status file
    config = ConnectorConfig()
    if work_dir:
        config.work_dir = work_dir
    
    connector_work_dir = Path(config.work_dir)
    status_file = connector_work_dir / "status.json"
    command_file = connector_work_dir / "command.json"
    response_file = connector_work_dir / "response.json"
    
    # Check if connector is running
    if not status_file.exists():
        # Start a temporary connector for this command
        connector = ShellConnector(config)
        try:
            connector.start()
            result = connector.execute_command(
                command=command,
                working_dir=working_dir,
                timeout=timeout
            )
            return result
        finally:
            connector.stop()
    
    # Use existing connector via file communication
    command_data = {
        "id": str(uuid.uuid4()),
        "command": command,
        "working_dir": working_dir,
        "timeout": timeout,
    }
    
    # Clean up any existing response file
    if response_file.exists():
        response_file.unlink()
    
    # Write command file
    with open(command_file, "w", encoding="utf-8") as f:
        json.dump(command_data, f, indent=2)
    
    # Wait for response
    max_wait = timeout + 10
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        if response_file.exists():
            try:
                with open(response_file, "r", encoding="utf-8") as f:
                    result_data = json.load(f)
                
                # Convert to CommandResult
                result = CommandResult(**result_data)
                response_file.unlink()
                return result
                
            except (json.JSONDecodeError, FileNotFoundError):
                time.sleep(0.1)
                continue
        
        time.sleep(0.2)
    
    # Timeout - create error result
    return CommandResult(
        success=False,
        stdout="",
        stderr="",
        exit_code=-1,
        command=command,
        execution_time=max_wait,
        command_id=command_data["id"],
        working_dir=working_dir,
        error=f"Helper timeout after {max_wait} seconds",
    )


def run_commands(
    commands: List[str],
    working_dir: Optional[str] = None,
    timeout: float = 30,
    stop_on_error: bool = True,
    work_dir: Optional[str] = None,
) -> List[CommandResult]:
    """
    Run multiple commands in sequence.
    
    Args:
        commands: List of shell commands to execute
        working_dir: Working directory for command execution
        timeout: Maximum execution time per command in seconds
        stop_on_error: Whether to stop execution on first error
        work_dir: Communication directory (defaults to ./claude_connector)
    
    Returns:
        List[CommandResult]: Results of all executed commands
    """
    results = []
    
    for i, command in enumerate(commands):
        print(f"Executing command {i+1}/{len(commands)}: {command}")
        
        result = run_command(
            command=command,
            working_dir=working_dir,
            timeout=timeout,
            work_dir=work_dir,
        )
        
        results.append(result)
        
        if not result.success and stop_on_error:
            print(f"Command failed, stopping execution: {result.error or 'Unknown error'}")
            break
    
    return results


def format_result(result: CommandResult) -> str:
    """Format command result for display."""
    output = []
    
    if result.success:
        output.append("✅ Command completed successfully")
    else:
        output.append("❌ Command failed")
        if result.error:
            output.append(f"Error: {result.error}")
    
    if result.stdout:
        output.append("\n📤 Output:")
        output.append(result.stdout)
    
    if result.stderr:
        output.append("\n⚠️ Error output:")
        output.append(result.stderr)
    
    output.append(f"\n🔢 Exit code: {result.exit_code}")
    output.append(f"⏱️ Execution time: {result.execution_time:.2f}s")
    
    return "\n".join(output)


def get_connector_status(work_dir: Optional[str] = None) -> dict:
    """Get the current connector status."""
    config = ConnectorConfig()
    if work_dir:
        config.work_dir = work_dir
    
    status_file = Path(config.work_dir) / "status.json"
    
    if not status_file.exists():
        return {"status": "not_running", "message": "Connector is not running"}
    
    try:
        with open(status_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"status": "error", "message": f"Error reading status: {e}"}