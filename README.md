# Claude Shell Connector

[![CI](https://github.com/yourusername/claude-shell-connector/workflows/CI/badge.svg)](https://github.com/yourusername/claude-shell-connector/actions)
[![PyPI version](https://badge.fury.io/py/claude-shell-connector.svg)](https://badge.fury.io/py/claude-shell-connector)
[![Python versions](https://img.shields.io/pypi/pyversions/claude-shell-connector.svg)](https://pypi.org/project/claude-shell-connector/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A secure and efficient bridge between Claude Desktop and shell environments, enabling seamless command execution across Cygwin, WSL, and native Unix shells.

## 🚀 Features

- **🔒 Secure Execution**: Sandboxed command execution with configurable timeouts
- **🐚 Multi-Shell Support**: Works with Cygwin, WSL, Bash, and PowerShell
- **📁 File-Based Communication**: Simple JSON-based command/response protocol
- **⚡ Real-Time Monitoring**: Live status updates and command tracking
- **🛠️ Developer Friendly**: Rich CLI interface and comprehensive Python API
- **🔧 Highly Configurable**: Customizable timeouts, working directories, and shell paths
- **📊 Comprehensive Logging**: Detailed execution logs and error reporting

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install claude-shell-connector
```

### From Source

```bash
git clone https://github.com/yourusername/claude-shell-connector.git
cd claude-shell-connector
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/yourusername/claude-shell-connector.git
cd claude-shell-connector
pip install -e .[dev]
pre-commit install
```

## 🏃 Quick Start

### 1. Start the Connector

```bash
# Start with default settings (auto-detects shell)
claude-shell start

# Or specify custom settings
claude-shell start --shell-path /usr/bin/bash --work-dir ./my-workspace --timeout 60
```

### 2. Execute Commands from Python

```python
from claude_shell_connector import run_command

# Execute a simple command
result = run_command("echo 'Hello, World!'")
if result.success:
    print(result.stdout)  # Output: Hello, World!

# Execute with custom settings
result = run_command(
    "ls -la /tmp",
    working_dir="/home/user/project",
    timeout=30
)
```

### 3. Use the Python API

```python
from claude_shell_connector import ShellConnector
from claude_shell_connector.config import ConnectorConfig

# Create custom configuration
config = ConnectorConfig(
    work_dir="./claude_workspace",
    shell_path="/usr/bin/bash",
    default_timeout=45
)

# Use as context manager
with ShellConnector(config) as connector:
    result = connector.execute_command("git status")
    print(f"Git status: {result.stdout}")
```

## 🔧 Configuration

### Environment Variables

```bash
export CLAUDE_SHELL_WORK_DIR="./claude_workspace"
export CLAUDE_SHELL_PATH="/usr/bin/bash"
export CLAUDE_SHELL_TIMEOUT="30"
export CLAUDE_SHELL_LOG_LEVEL="INFO"
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Note**: This project is not officially affiliated with Anthropic or Claude AI. It's a community-driven tool to enhance Claude Desktop functionality.