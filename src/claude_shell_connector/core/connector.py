"""Core connector for Claude Shell Connector."""

import json
import logging
import os
import subprocess
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

# Optional imports for Cygwin compatibility
try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    
    # Create dummy classes for compatibility
    class FileSystemEventHandler:
        pass
    
    class Observer:
        def __init__(self):
            pass
        def schedule(self, *args, **kwargs):
            pass
        def start(self):
            pass
        def stop(self):
            pass
        def join(self):
            pass

from ..config.settings import ConnectorConfig
from .exceptions import (
    ClaudeShellConnectorError,
    CommandExecutionError,
    ConnectorNotRunningError,
    InvalidCommandError,
    TimeoutError,
)

logger = logging.getLogger(__name__)


class CommandResult(BaseModel):
    """Result of a shell command execution."""
    
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int
    command: str
    execution_time: float = Field(ge=0.0)
    timestamp: datetime = Field(default_factory=datetime.now)
    command_id: str
    working_dir: Optional[str] = None
    error: Optional[str] = None
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }


class CommandFileHandler(FileSystemEventHandler):
    """Handles command file events."""
    
    def __init__(self, connector):
        super().__init__()
        self.connector = connector
    
    def on_created(self, event):
        if event.src_path.endswith("command.json"):
            time.sleep(0.1)  # Wait for file to be fully written
            self.connector.process_command_file()


class PollingFileWatcher:
    """Fallback file watcher for when watchdog is not available."""
    
    def __init__(self, connector, watch_dir):
        self.connector = connector
        self.watch_dir = Path(watch_dir)
        self.command_file = self.watch_dir / "command.json"
        self.running = False
        self.last_mtime = None
    
    def start(self):
        """Start polling for file changes."""
        self.running = True
        
        # Run polling in a separate thread would be ideal,
        # but for simplicity, we'll use a simple approach
        import threading
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop polling."""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1)
    
    def _poll_loop(self):
        """Poll for file changes."""
        while self.running:
            try:
                if self.command_file.exists():
                    mtime = self.command_file.stat().st_mtime
                    if self.last_mtime is None or mtime > self.last_mtime:
                        self.last_mtime = mtime
                        time.sleep(0.1)  # Wait for file to be fully written
                        if self.command_file.exists():  # Check again
                            self.connector.process_command_file()
                
                time.sleep(0.5)  # Poll every 500ms
                
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(1)


class ShellConnector:
    """Main connector class for shell command execution."""
    
    def __init__(self, config: Optional[ConnectorConfig] = None):
        self.config = config or ConnectorConfig()
        self.work_dir = Path(self.config.work_dir)
        self.work_dir.mkdir(exist_ok=True)
        
        # Communication files
        self.command_file = self.work_dir / "command.json"
        self.response_file = self.work_dir / "response.json"
        self.status_file = self.work_dir / "status.json"
        
        # State
        self._running = False
        self._commands_executed = 0
        self.observer = None
        self.file_watcher = None
        self._start_time = None
        
        # Detect shell type and set appropriate execution method
        self._detect_shell_type()
        
        self._update_status("ready", "Connector initialized")
        logger.info(f"Connector initialized with work_dir: {self.work_dir}")
        
        if not WATCHDOG_AVAILABLE:
            logger.warning("Watchdog not available, using polling file watcher")
    
    def _detect_shell_type(self):
        """Detect shell type and set execution parameters."""
        shell_name = self.config.shell_path.name.lower()
        shell_path_str = str(self.config.shell_path).lower()
        
        # Set shell-specific parameters
        if "alt-bash" in shell_name:
            # alt-bash might have issues with -l (login shell)
            self.shell_args = ["-c"]
            self.shell_type = "alt-bash"
        elif "bash" in shell_name:
            # Regular bash - try without -l first for Cygwin compatibility
            self.shell_args = ["-c"]
            self.shell_type = "bash"
        elif "sh" in shell_name:
            self.shell_args = ["-c"]
            self.shell_type = "sh"
        elif "cmd" in shell_name:
            self.shell_args = ["/c"]
            self.shell_type = "cmd"
        elif "powershell" in shell_name:
            self.shell_args = ["-Command"]
            self.shell_type = "powershell"
        else:
            # Default fallback
            self.shell_args = ["-c"]
            self.shell_type = "unknown"
        
        logger.info(f"Detected shell type: {self.shell_type}, args: {self.shell_args}")
    
    def start(self):
        """Start the connector."""
        if self._running:
            raise ClaudeShellConnectorError("Connector is already running")
        
        self._start_time = datetime.now()
        self._running = True
        
        # Set up file watcher
        if WATCHDOG_AVAILABLE:
            try:
                event_handler = CommandFileHandler(self)
                self.observer = Observer()
                self.observer.schedule(event_handler, str(self.work_dir), recursive=False)
                self.observer.start()
                logger.info("Using watchdog file watcher")
            except Exception as e:
                logger.warning(f"Watchdog failed, falling back to polling: {e}")
                self._setup_polling_watcher()
        else:
            self._setup_polling_watcher()
        
        self._update_status("ready", "Connector started")
        logger.info("Connector started successfully")
    
    def _setup_polling_watcher(self):
        """Set up polling-based file watcher."""
        self.file_watcher = PollingFileWatcher(self, self.work_dir)
        self.file_watcher.start()
        logger.info("Using polling file watcher")
    
    def stop(self):
        """Stop the connector."""
        if not self._running:
            return
        
        self._running = False
        
        if self.observer:
            try:
                self.observer.stop()
                self.observer.join()
            except Exception as e:
                logger.error(f"Error stopping observer: {e}")
            self.observer = None
        
        if self.file_watcher:
            try:
                self.file_watcher.stop()
            except Exception as e:
                logger.error(f"Error stopping file watcher: {e}")
            self.file_watcher = None
        
        self._update_status("stopped", "Connector stopped")
        logger.info("Connector stopped")
    
    def is_running(self) -> bool:
        """Check if connector is running."""
        return self._running
    
    def execute_command(
        self,
        command: str,
        working_dir: Optional[str] = None,
        timeout: Optional[float] = None,
        command_id: Optional[str] = None,
    ) -> CommandResult:
        """Execute a command directly."""
        if not self._running:
            raise ConnectorNotRunningError("Connector is not running")
        
        if not command.strip():
            raise InvalidCommandError("Command cannot be empty")
        
        command_id = command_id or str(uuid.uuid4())
        timeout = timeout or self.config.default_timeout
        
        logger.info(f"Executing command {command_id}: {command}")
        self._update_status("executing", f"Running: {command[:50]}...")
        
        start_time = time.time()
        
        try:
            # Prepare environment with encoding fixes
            env = os.environ.copy()
            env.update({
                "PYTHONIOENCODING": "utf-8",
                "LC_ALL": "C.UTF-8",
                "LANG": "C.UTF-8",
            })
            
            if "cygwin" in str(self.config.shell_path).lower():
                env["CYGWIN"] = "nodosfilewarning"
            
            # Handle working directory for Cygwin
            final_command = command
            if working_dir and "cygwin" in str(self.config.shell_path).lower():
                if Path(working_dir).is_absolute() and ":" in working_dir:
                    # Convert Windows path to Cygwin path
                    drive = working_dir[0].lower()
                    path = working_dir[2:].replace("\\", "/")
                    cygwin_dir = f"/cygdrive/{drive}/{path}"
                    final_command = f"cd '{cygwin_dir}' && {command}"
            elif working_dir:
                final_command = f"cd '{working_dir}' && {command}"
            
            # Build command arguments based on shell type
            cmd_args = [str(self.config.shell_path)] + self.shell_args + [final_command]
            
            logger.debug(f"Executing: {cmd_args}")
            
            # Execute command with improved settings
            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                env=env,
                # Prevent shell from hanging on input
                close_fds=True,
                # Set process group for better cleanup
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None,
            )
            
            # Immediately close stdin to prevent hanging
            if process.stdin:
                process.stdin.close()
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                # Force kill the process and its children
                try:
                    if hasattr(os, 'killpg'):
                        os.killpg(os.getpgid(process.pid), 9)
                    else:
                        process.kill()
                except:
                    pass
                
                try:
                    stdout, stderr = process.communicate(timeout=2)
                except subprocess.TimeoutExpired:
                    stdout, stderr = "", ""
                
                execution_time = time.time() - start_time
                
                result = CommandResult(
                    success=False,
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=-1,
                    command=command,
                    execution_time=execution_time,
                    command_id=command_id,
                    working_dir=working_dir,
                    error=f"Command timed out after {timeout} seconds",
                )
                
                logger.error(f"Command {command_id} timed out")
                self._update_status("ready", "Command timed out")
                return result
            
            execution_time = time.time() - start_time
            
            result = CommandResult(
                success=process.returncode == 0,
                stdout=stdout,
                stderr=stderr,
                exit_code=process.returncode,
                command=command,
                execution_time=execution_time,
                command_id=command_id,
                working_dir=working_dir,
            )
            
            self._commands_executed += 1
            
            if result.success:
                logger.info(f"Command {command_id} completed successfully")
                self._update_status("ready", "Command completed")
            else:
                logger.warning(f"Command {command_id} failed")
                self._update_status("ready", f"Command failed: exit code {result.exit_code}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            result = CommandResult(
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
            
            logger.error(f"Command {command_id} failed: {e}")
            self._update_status("error", f"Execution error: {e}")
            return result
    
    def process_command_file(self):
        """Process command from file."""
        if not self.command_file.exists():
            return
        
        try:
            with open(self.command_file, "r", encoding="utf-8") as f:
                command_data = json.load(f)
            
            command = command_data.get("command", "")
            working_dir = command_data.get("working_dir")
            timeout = command_data.get("timeout", self.config.default_timeout)
            command_id = command_data.get("id", str(uuid.uuid4()))
            
            result = self.execute_command(
                command=command,
                working_dir=working_dir,
                timeout=timeout,
                command_id=command_id,
            )
            
            # Write response
            with open(self.response_file, "w", encoding="utf-8") as f:
                json.dump(result.dict(), f, indent=2)
            
            # Remove command file
            self.command_file.unlink()
            
        except Exception as e:
            logger.error(f"Error processing command file: {e}")
            
            error_result = {
                "success": False,
                "error": f"Connector error: {e}",
                "stdout": "",
                "stderr": "",
                "exit_code": -1,
                "command": command_data.get("command", "unknown") if 'command_data' in locals() else "unknown",
                "execution_time": 0.0,
                "timestamp": datetime.now().isoformat(),
                "command_id": command_data.get("id", "unknown") if 'command_data' in locals() else "unknown",
                "working_dir": None,
            }
            
            try:
                with open(self.response_file, "w", encoding="utf-8") as f:
                    json.dump(error_result, f, indent=2)
            except Exception as write_error:
                logger.error(f"Failed to write error response: {write_error}")
    
    def _update_status(self, status: str, message: str = ""):
        """Update status file."""
        uptime = 0.0
        if self._start_time:
            uptime = (datetime.now() - self._start_time).total_seconds()
        
        status_data = {
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "work_dir": str(self.work_dir),
            "shell_path": str(self.config.shell_path),
            "shell_type": getattr(self, 'shell_type', 'unknown'),
            "shell_args": getattr(self, 'shell_args', []),
            "commands_executed": self._commands_executed,
            "uptime": uptime,
            "watchdog_available": WATCHDOG_AVAILABLE,
        }
        
        try:
            with open(self.status_file, "w", encoding="utf-8") as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()