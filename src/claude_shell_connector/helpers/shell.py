"""Simple, direct shell execution helpers that bypass connector complexity."""

import os
import subprocess
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..core.connector import CommandResult


def run_command_direct(
    command: str,
    working_dir: Optional[str] = None,
    timeout: float = 30,
    shell_path: Optional[str] = None,
) -> CommandResult:
    """
    Run a command directly without using the connector service.
    This bypasses all file watching and connector complexity.
    """
    command_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Auto-detect shell if not provided
    if shell_path is None:
        # Simple shell detection for Cygwin
        shells_to_try = [
            "/bin/bash",
            "/usr/bin/bash", 
            "/bin/alt-bash",
            "/bin/sh"
        ]
        
        shell_path = None
        for shell in shells_to_try:
            if Path(shell).exists():
                shell_path = shell
                break
        
        if shell_path is None:
            return CommandResult(
                success=False,
                stdout="",
                stderr="",
                exit_code=-1,
                command=command,
                execution_time=0.0,
                command_id=command_id,
                working_dir=working_dir,
                error="No suitable shell found",
            )
    
    try:
        # Prepare environment
        env = os.environ.copy()
        env.update({
            "PYTHONIOENCODING": "utf-8",
            "LC_ALL": "C.UTF-8",
            "LANG": "C.UTF-8",
            "CYGWIN": "nodosfilewarning",
        })
        
        # Handle working directory
        final_command = command
        if working_dir:
            if "cygwin" in shell_path.lower() and Path(working_dir).is_absolute() and ":" in working_dir:
                # Convert Windows path to Cygwin path
                drive = working_dir[0].lower()
                path = working_dir[2:].replace("\\", "/")
                cygwin_dir = f"/cygdrive/{drive}/{path}"
                final_command = f"cd '{cygwin_dir}' && {command}"
            else:
                final_command = f"cd '{working_dir}' && {command}"
        
        # Execute with the simplest possible method
        try:
            # Method 1: Try with minimal subprocess setup
            process = subprocess.Popen(
                [shell_path, "-c", final_command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,  # No stdin to prevent hanging
                text=True,
                env=env,
                start_new_session=True,  # Detach from parent
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            execution_time = time.time() - start_time
            
            return CommandResult(
                success=process.returncode == 0,
                stdout=stdout,
                stderr=stderr,
                exit_code=process.returncode,
                command=command,
                execution_time=execution_time,
                command_id=command_id,
                working_dir=working_dir,
            )
            
        except subprocess.TimeoutExpired:
            try:
                process.kill()
                process.wait(timeout=2)
            except:
                pass
            
            execution_time = time.time() - start_time
            
            return CommandResult(
                success=False,
                stdout="",
                stderr="",
                exit_code=-1,
                command=command,
                execution_time=execution_time,
                command_id=command_id,
                working_dir=working_dir,
                error=f"Command timed out after {timeout} seconds",
            )
            
    except Exception as e:
        execution_time = time.time() - start_time
        
        return CommandResult(
            success=False,
            stdout="",
            stderr="",
            exit_code=-1,
            command=command,
            execution_time=execution_time,
            command_id=command_id,
            working_dir=working_dir,
            error=str(e),
        )


def run_command_fallback(
    command: str,
    working_dir: Optional[str] = None,
    timeout: float = 30,
) -> CommandResult:
    """
    Fallback method using os.popen for cases where subprocess fails.
    """
    command_id = str(uuid.uuid4())
    start_time = time.time()
    
    try:
        # Prepare command with working directory
        if working_dir:
            full_command = f"cd '{working_dir}' && {command}"
        else:
            full_command = command
        
        # Use os.popen as fallback
        with os.popen(full_command) as pipe:
            stdout = pipe.read()
        
        execution_time = time.time() - start_time
        
        return CommandResult(
            success=True,  # os.popen doesn't provide exit code easily
            stdout=stdout,
            stderr="",
            exit_code=0,
            command=command,
            execution_time=execution_time,
            command_id=command_id,
            working_dir=working_dir,
        )
        
    except Exception as e:
        execution_time = time.time() - start_time
        
        return CommandResult(
            success=False,
            stdout="",
            stderr="",
            exit_code=-1,
            command=command,
            execution_time=execution_time,
            command_id=command_id,
            working_dir=working_dir,
            error=str(e),
        )


# Update the main run_command function to use direct execution
def run_command(
    command: str,
    working_dir: Optional[str] = None,
    timeout: float = 30,
    work_dir: Optional[str] = None,
) -> CommandResult:
    """
    Run a single command using direct execution (bypassing connector complexity).
    """
    # Try direct execution first
    result = run_command_direct(command, working_dir, timeout)
    
    # If direct execution times out, try fallback method
    if not result.success and "timeout" in (result.error or "").lower():
        print(f"Direct execution timed out, trying fallback method...")
        result = run_command_fallback(command, working_dir, timeout)
    
    return result


def run_commands(
    commands: List[str],
    working_dir: Optional[str] = None,
    timeout: float = 30,
    stop_on_error: bool = True,
    work_dir: Optional[str] = None,
) -> List[CommandResult]:
    """
    Run multiple commands in sequence using direct execution.
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
    from ..config.settings import ConnectorConfig
    
    config = ConnectorConfig()
    if work_dir:
        config.work_dir = work_dir
    
    status_file = Path(config.work_dir) / "status.json"
    
    if not status_file.exists():
        return {"status": "not_running", "message": "Connector is not running"}
    
    try:
        with open(status_file, "r", encoding="utf-8") as f:
            import json
            return json.load(f)
    except Exception as e:
        return {"status": "error", "message": f"Error reading status: {e}"}