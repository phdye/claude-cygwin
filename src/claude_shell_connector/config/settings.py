"""Configuration settings for Claude Shell Connector."""

import os
import platform
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, validator


class ConnectorConfig(BaseModel):
    """Configuration for the Claude Shell Connector."""
    
    work_dir: str = Field(default_factory=lambda: str(Path.cwd() / "claude_connector"))
    shell_path: Path = Field(default_factory=lambda: ConnectorConfig._detect_shell())
    default_timeout: float = Field(default=30.0, ge=1.0, le=300.0)
    max_output_size: int = Field(default=1024*1024, ge=1024)  # 1MB default
    log_level: str = Field(default="INFO")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        arbitrary_types_allowed = True
    
    @validator('work_dir')
    def validate_work_dir(cls, v: str) -> str:
        """Ensure work directory is absolute and create if needed."""
        path = Path(v).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return str(path)
    
    @validator('shell_path')
    def validate_shell_path(cls, v: Path) -> Path:
        """Validate shell path exists and is executable."""
        if not v.exists():
            raise ValueError(f"Shell not found at {v}")
        return v
    
    @staticmethod
    def _detect_shell() -> Path:
        """Auto-detect the best available shell."""
        system = platform.system().lower()
        
        # Common shell paths by system
        shell_candidates = {
            'windows': [
                Path(r"C:\cygwin64\bin\bash.exe"),
                Path(r"C:\cygwin\bin\bash.exe"),
                Path(r"C:\msys64\usr\bin\bash.exe"),
                Path(r"C:\Program Files\Git\bin\bash.exe"),
                Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"),
                Path(r"C:\Windows\System32\cmd.exe"),
            ],
            'linux': [
                Path("/bin/bash"),
                Path("/usr/bin/bash"),
                Path("/bin/sh"),
                Path("/usr/bin/sh"),
            ],
            'darwin': [  # macOS
                Path("/bin/bash"),
                Path("/usr/bin/bash"),
                Path("/bin/zsh"),
                Path("/usr/bin/zsh"),
                Path("/bin/sh"),
            ],
        }
        
        # Try to find shell from PATH first
        shell_env = os.environ.get('SHELL')
        if shell_env and Path(shell_env).exists():
            return Path(shell_env)
        
        # Try system-specific candidates
        candidates = shell_candidates.get(system, shell_candidates['linux'])
        for candidate in candidates:
            if candidate.exists():
                return candidate
        
        # Fallback - this will trigger validation error if not found
        return Path("/bin/bash")
    
    @classmethod
    def from_env(cls) -> "ConnectorConfig":
        """Create configuration from environment variables."""
        return cls(
            work_dir=os.environ.get("CLAUDE_SHELL_WORK_DIR", cls().work_dir),
            shell_path=Path(os.environ.get("CLAUDE_SHELL_PATH", str(cls._detect_shell()))),
            default_timeout=float(os.environ.get("CLAUDE_SHELL_TIMEOUT", "30")),
            max_output_size=int(os.environ.get("CLAUDE_SHELL_MAX_OUTPUT", str(1024*1024))),
            log_level=os.environ.get("CLAUDE_SHELL_LOG_LEVEL", "INFO"),
        )