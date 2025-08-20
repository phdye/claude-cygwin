# Troubleshooting Guide

This guide covers common issues and their solutions when using Claude Shell Connector.

## 🔧 Installation Issues

### Python Version Error
**Problem**: `Python 3.X is not supported`

**Solution**:
```bash
# Check your Python version
python --version

# Install Python 3.8+ if needed
# Windows: Download from python.org
# Ubuntu: sudo apt install python3.8
# macOS: brew install python@3.8
```

### Shell Not Found Error
**Problem**: `Shell not found at /path/to/shell`

**Solutions**:
1. **Install missing shell**:
   - **Cygwin**: https://www.cygwin.com/
   - **Git Bash**: https://gitforwindows.org/
   - **WSL**: `wsl --install`

2. **Specify shell path manually**:
   ```bash
   claude-shell start --shell-path /usr/bin/bash
   ```

3. **Check available shells**:
   ```bash
   claude-shell test
   ```

### Permission Denied
**Problem**: Permission errors when creating work directory

**Solution**:
```bash
# Create directory manually with correct permissions
mkdir -p ~/.claude-shell-connector
chmod 755 ~/.claude-shell-connector

# Or specify different work directory
claude-shell start --work-dir ./my-workspace
```

## 🚀 Runtime Issues

### Connector Won't Start
**Problem**: `Connector is already running` or startup fails

**Solutions**:
1. **Check if already running**:
   ```bash
   claude-shell status
   ```

2. **Kill existing process**:
   ```bash
   # Find and kill process
   ps aux | grep claude-shell
   kill <PID>
   ```

3. **Clean work directory**:
   ```bash
   rm -rf ~/.claude-shell-connector/workspace
   ```

### Commands Timeout
**Problem**: Commands timeout before completion

**Solutions**:
1. **Increase timeout**:
   ```bash
   claude-shell exec "long-command" --timeout 120
   ```

2. **Check system resources**:
   ```bash
   # Check CPU/memory usage
   top
   htop
   
   # Check disk space
   df -h
   ```

3. **Optimize command**:
   ```bash
   # Break into smaller commands
   claude-shell exec "command1"
   claude-shell exec "command2"
   ```

### Command Execution Fails
**Problem**: Commands fail with non-zero exit codes

**Solutions**:
1. **Test command manually**:
   ```bash
   # Test in your shell first
   /usr/bin/bash -c "your-command"
   ```

2. **Check command syntax**:
   ```bash
   # Escape special characters
   claude-shell exec "echo 'hello world'"
   
   # Use proper quoting
   claude-shell exec 'echo "nested quotes"'
   ```

3. **Debug with verbose output**:
   ```python
   from claude_shell_connector import run_command
   result = run_command("failing-command")
   print(f"Exit code: {result.exit_code}")
   print(f"Stdout: {result.stdout}")
   print(f"Stderr: {result.stderr}")
   print(f"Error: {result.error}")
   ```

## 🐞 Common Errors

### `ModuleNotFoundError: No module named 'claude_shell_connector'`
**Cause**: Package not installed or wrong environment

**Solution**:
```bash
# Install package
pip install -e .

# Or check virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Verify installation
python -c "import claude_shell_connector; print('OK')"
```

### `FileNotFoundError: command not found`
**Cause**: Command not in PATH or shell environment

**Solution**:
```bash
# Check if command exists
which your-command

# Use full path
claude-shell exec "/usr/bin/your-command"

# Set environment variables
export PATH="/custom/path:$PATH"
claude-shell start
```

### `PermissionError: Access denied`
**Cause**: Insufficient permissions for command or files

**Solution**:
```bash
# Check file permissions
ls -la file-or-directory

# Make executable
chmod +x script.sh

# Run with different user (if appropriate)
sudo claude-shell exec "privileged-command"
```

### Connection Refused or Network Errors
**Cause**: Firewall or network restrictions

**Solution**:
```bash
# Check firewall settings
# Ensure localhost communication is allowed

# Test basic connectivity
ping localhost
telnet localhost 22
```

## 🔍 Debugging

### Enable Debug Logging
```python
import logging
from claude_shell_connector import configure_logging

# Enable debug output
configure_logging(level="DEBUG")

# Or via environment
export CLAUDE_SHELL_LOG_LEVEL=DEBUG
claude-shell start
```

### Trace Command Execution
```python
from claude_shell_connector import ShellConnector
from claude_shell_connector.config import ConnectorConfig

config = ConnectorConfig()
config.log_level = "DEBUG"

with ShellConnector(config) as connector:
    result = connector.execute_command("your-command")
    print(f"Execution time: {result.execution_time}")
    print(f"Command ID: {result.command_id}")
```

### Check System Resources
```bash
# Memory usage
free -h

# Disk space
df -h

# Process information
ps aux | grep python

# Network connections
netstat -tulpn | grep python
```

## 🔧 Platform-Specific Issues

### Cygwin
**For comprehensive Cygwin support, see**: [Cygwin Compatibility Guide](cygwin-compatibility.md)

**Quick fixes**:
- **Package install fails**: Use `python setup_cygwin.py`
- **Import errors**: Set `export PYTHONPATH=$(pwd)/src:$PYTHONPATH`
- **Path issues**: Use `/cygdrive/c/` format or let connector auto-convert
- **File watching**: Automatically falls back to polling

### Windows/Native
**Issue**: Path conversion problems

**Solution**:
```bash
# Use forward slashes or raw strings
working_dir = r"C:\Users\username\"
# or
working_dir = "C:/Users/username/"
```

### WSL (Windows Subsystem for Linux)
**Issue**: Can't access Windows files

**Solution**:
```bash
# Access Windows files via /mnt/
ls /mnt/c/Users/

# Or use WSL path
wslpath "C:\Windows"
```

### macOS
**Issue**: Shell path differences

**Solution**:
```bash
# Check available shells
cat /etc/shells

# Use Homebrew shells
/opt/homebrew/bin/bash
```

## 📊 Performance Issues

### Slow Command Execution
**Causes and Solutions**:

1. **Large output**: Increase `max_output_size`
2. **Network commands**: Increase timeout
3. **Heavy computation**: Run in background
4. **Many files**: Use efficient commands (`find` vs `ls -R`)

### Memory Usage
**Monitor and optimize**:
```bash
# Monitor memory usage
ps aux | grep claude-shell

# Limit output size
result = run_command("command", timeout=30)
if len(result.stdout) > 1000000:  # 1MB
    print("Output too large")
```

## 🆘 Getting Help

If you're still having issues:

1. **Check the logs**: Look in the work directory for `connector.log`
2. **Search issues**: [GitHub Issues](https://github.com/yourusername/claude-shell-connector/issues)
3. **Create bug report**: Include:
   - Operating system and version
   - Python version
   - Shell type and version
   - Complete error message
   - Steps to reproduce
   - Configuration used

4. **Community support**: [GitHub Discussions](https://github.com/yourusername/claude-shell-connector/discussions)

## 📚 Additional Resources

- **[Configuration Guide](configuration.md)** - Detailed configuration options
- **[API Reference](api-reference.md)** - Complete API documentation
- **[Examples](../examples/)** - Working examples
- **[Contributing](../CONTRIBUTING.md)** - How to contribute improvements