#!/usr/bin/env python3
"""
Installation and setup script for Claude Shell Connector development environment.
"""

import os
import subprocess
import sys
import platform
from pathlib import Path


def run_command(cmd, check=True, shell=False):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd if shell else cmd.split(),
            check=check,
            capture_output=True,
            text=True,
            shell=shell
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_python_version():
    """Check if Python version is supported."""
    version = sys.version_info
    if version < (3, 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported")
        print("Please install Python 3.8 or higher")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is supported")


def check_git():
    """Check if git is available."""
    try:
        result = run_command("git --version")
        print(f"✅ Git is available: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Git is not available")
        return False


def check_shell():
    """Check available shell environments."""
    shells_found = []
    
    system = platform.system().lower()
    
    shell_candidates = {
        'windows': [
            (r"C:\cygwin64\bin\bash.exe", "Cygwin 64-bit"),
            (r"C:\cygwin\bin\bash.exe", "Cygwin 32-bit"),
            (r"C:\msys64\usr\bin\bash.exe", "MSYS2"),
            (r"C:\Program Files\Git\bin\bash.exe", "Git Bash"),
        ],
        'linux': [
            ("/bin/bash", "Bash"),
            ("/usr/bin/bash", "Bash"),
            ("/bin/sh", "Shell"),
        ],
        'darwin': [
            ("/bin/bash", "Bash"),
            ("/bin/zsh", "Zsh"),
            ("/usr/bin/bash", "Bash"),
        ],
    }
    
    candidates = shell_candidates.get(system, shell_candidates['linux'])
    
    for shell_path, name in candidates:
        if Path(shell_path).exists():
            shells_found.append((shell_path, name))
            print(f"✅ Found {name}: {shell_path}")
    
    if not shells_found:
        print("⚠️  No compatible shells found")
        if system == 'windows':
            print("Consider installing:")
            print("  - Cygwin: https://www.cygwin.com/")
            print("  - Git for Windows: https://gitforwindows.org/")
            print("  - WSL: https://docs.microsoft.com/en-us/windows/wsl/")
    
    return shells_found


def setup_virtual_environment():
    """Set up virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return
    
    print("🔧 Creating virtual environment...")
    run_command(f"{sys.executable} -m venv venv")
    
    # Activate script path
    if platform.system() == "Windows":
        activate_script = venv_path / "Scripts" / "activate.bat"
        pip_path = venv_path / "Scripts" / "pip.exe"
    else:
        activate_script = venv_path / "bin" / "activate"
        pip_path = venv_path / "bin" / "pip"
    
    print(f"✅ Virtual environment created")
    print(f"   Activate with: {activate_script}")
    
    return pip_path


def install_dependencies(pip_path=None):
    """Install development dependencies."""
    pip_cmd = str(pip_path) if pip_path else "pip"
    
    print("🔧 Installing dependencies...")
    
    # Upgrade pip first
    run_command(f"{pip_cmd} install --upgrade pip")
    
    # Install package in development mode
    run_command(f"{pip_cmd} install -e .[dev]")
    
    print("✅ Dependencies installed")


def setup_pre_commit():
    """Set up pre-commit hooks."""
    if not check_git():
        print("⚠️  Skipping pre-commit setup (git not available)")
        return
    
    try:
        print("🔧 Setting up pre-commit hooks...")
        run_command("pre-commit install")
        print("✅ Pre-commit hooks installed")
    except subprocess.CalledProcessError:
        print("⚠️  Failed to install pre-commit hooks")


def run_tests():
    """Run basic tests to verify setup."""
    print("🧪 Running basic tests...")
    try:
        result = run_command("python -m pytest tests/test_basic.py -v", check=False)
        if result.returncode == 0:
            print("✅ Basic tests passed")
        else:
            print("⚠️  Some tests failed (this might be expected)")
    except FileNotFoundError:
        print("⚠️  pytest not available, skipping tests")


def create_config_example():
    """Create example configuration file."""
    config_dir = Path.home() / ".claude-shell-connector"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "config.example.yaml"
    
    if config_file.exists():
        return
    
    config_content = """# Claude Shell Connector Configuration Example
# Copy this to config.yaml and customize as needed

work_dir: "~/.claude-shell-connector/workspace"
shell_path: "/usr/bin/bash"  # Auto-detected if not specified
default_timeout: 30
max_output_size: 1048576  # 1MB
log_level: "INFO"

# Security settings (optional)
security:
  allowed_commands: []  # Empty = allow all
  forbidden_patterns: ["rm -rf", "sudo", "passwd"]
  max_execution_time: 300
"""
    
    with open(config_file, "w") as f:
        f.write(config_content)
    
    print(f"✅ Created example config: {config_file}")


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    
    print("\n📋 Next steps:")
    print("1. Activate virtual environment:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2. Test the installation:")
    print("   claude-shell test")
    
    print("\n3. Start the connector:")
    print("   claude-shell start")
    
    print("\n4. Use in Python:")
    print("   from claude_shell_connector import run_command")
    print("   result = run_command('echo Hello')")
    print("   print(result.stdout)")
    
    print("\n5. Development commands:")
    print("   make test      # Run tests")
    print("   make lint      # Check code quality")
    print("   make format    # Format code")
    
    print("\n📚 Documentation:")
    print("   README.md         # Overview and usage")
    print("   CONTRIBUTING.md   # Development guidelines")
    print("   examples/         # Usage examples")
    
    print("\n" + "="*60)


def main():
    """Main setup function."""
    print("Claude Shell Connector - Development Setup")
    print("="*50)
    
    # Check prerequisites
    check_python_version()
    has_git = check_git()
    shells = check_shell()
    
    # Setup development environment
    pip_path = setup_virtual_environment()
    install_dependencies(pip_path)
    
    if has_git:
        setup_pre_commit()
    
    # Create configuration example
    create_config_example()
    
    # Run basic verification
    run_tests()
    
    # Show next steps
    print_next_steps()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)