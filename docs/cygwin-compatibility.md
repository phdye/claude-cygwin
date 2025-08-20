# Cygwin Compatibility Issues and Solutions

This document specifically addresses issues when running Claude Shell Connector on Cygwin.

## 🐧 Known Cygwin Limitations

### 1. Package Installation Issues

**Problem**: `platform cygwin is not supported`

**Affected packages**:
- `psutil` - Process utilities
- `watchdog` - File system monitoring
- Some other binary packages

**Solutions**:

#### Option A: Use Cygwin-compatible setup
```bash
# Use the Cygwin-specific setup script
python setup_cygwin.py
```

#### Option B: Manual installation
```bash
# Install only compatible dependencies
pip install click pydantic rich typing-extensions

# Set Python path
export PYTHONPATH=$(pwd)/src:$PYTHONPATH

# Test import
python -c "import claude_shell_connector; print('Success')"
```

#### Option C: Skip problematic packages
```bash
# Install base package without optional dependencies
pip install --no-deps -e .

# Install compatible dependencies manually
pip install click pydantic rich
```

### 2. File Watching Limitations

**Problem**: Watchdog doesn't work properly on Cygwin

**Solution**: The connector automatically falls back to polling-based file watching:

```python
# This happens automatically in the connector
if not WATCHDOG_AVAILABLE:
    # Use polling instead of native file events
    self.file_watcher = PollingFileWatcher(self, self.work_dir)
```

**Performance impact**: Polling is slightly slower but still functional.

### 3. Path Conversion Issues

**Problem**: Windows paths vs Cygwin paths

**Solutions**:

```bash
# Use Cygwin paths
cd /cygdrive/c/Users/username/project

# Convert Windows paths to Cygwin paths
cygpath -u "C:\Users\username\project"

# Convert Cygwin paths to Windows paths  
cygpath -w "/home/username/project"
```

**In the connector**: Automatic conversion is handled for working directories:
```python
# This happens automatically
if "cygwin" in str(self.config.shell_path).lower():
    if Path(working_dir).is_absolute() and ":" in working_dir:
        drive = working_dir[0].lower()
        path = working_dir[2:].replace("\\", "/")
        cygwin_dir = f"/cygdrive/{drive}/{path}"
        command = f"cd '{cygwin_dir}' && {command}"
```

## 🔧 Cygwin-Specific Setup

### Quick Setup
```bash
# Clone/navigate to project
cd ~/my-repos/claude-cygwin

# Run Cygwin setup
python setup_cygwin.py

# Use the launcher
./claude-shell-cygwin test
```

### Manual Setup
```bash
# Install Python dependencies
pip install click pydantic rich

# Set environment
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
export CYGWIN=nodosfilewarning

# Test
python -c "from claude_shell_connector import run_command; print('OK')"
```

### Using the Launcher Script

The setup creates a `claude-shell-cygwin` launcher that handles Python path:

```bash
# Test connectivity
./claude-shell-cygwin test

# Check status  
./claude-shell-cygwin status

# Execute command
./claude-shell-cygwin exec "pwd"
```

## 🐛 Common Cygwin Errors

### ImportError: No module named 'claude_shell_connector'

**Cause**: Python path not set correctly

**Solution**:
```bash
# Method 1: Set PYTHONPATH
export PYTHONPATH=$(pwd)/src:$PYTHONPATH

# Method 2: Use launcher script
./claude-shell-cygwin

# Method 3: Modify Python path in script
python -c "
import sys
sys.path.insert(0, 'src')
from claude_shell_connector import run_command
"
```

### Command execution fails with path errors

**Cause**: Windows/Cygwin path confusion

**Solution**:
```python
from claude_shell_connector import run_command

# Use Cygwin paths
result = run_command("ls /cygdrive/c/Users")

# Or let the connector handle conversion
result = run_command("ls", working_dir="C:\\Users")
```

### Permission denied errors

**Cause**: Cygwin permission system

**Solution**:
```bash
# Check permissions
ls -la

# Fix executable permissions
chmod +x script.sh

# Set Cygwin options
export CYGWIN=nodosfilewarning
```

### Process monitoring not working

**Cause**: psutil not available on Cygwin

**Workaround**: Use shell commands instead:
```python
from claude_shell_connector import run_command

# Instead of psutil, use shell commands
result = run_command("ps aux")
result = run_command("df -h")
result = run_command("free -m")  # If available
```

## 🎯 Best Practices for Cygwin

### 1. Environment Setup
```bash
# Add to ~/.bashrc
export PYTHONPATH=$HOME/my-repos/claude-cygwin/src:$PYTHONPATH
export CYGWIN=nodosfilewarning
export PATH=$HOME/my-repos/claude-cygwin:$PATH
```

### 2. Path Handling
```python
# Always use forward slashes in Cygwin
working_dir = "/cygdrive/c/projects/myproject"

# Or use pathlib for cross-platform compatibility
from pathlib import Path
working_dir = str(Path("/cygdrive/c/projects/myproject"))
```

### 3. Shell Commands
```python
# Prefer Cygwin-native commands
run_command("find . -name '*.py'")  # Instead of Windows findstr
run_command("grep -r 'pattern' .")  # Instead of Windows findstr
run_command("ls -la")              # Instead of Windows dir
```

### 4. Error Handling
```python
from claude_shell_connector import run_command

result = run_command("some-command")

if not result.success:
    print(f"Command failed: {result.error}")
    print(f"Exit code: {result.exit_code}")
    print(f"Stderr: {result.stderr}")
    
    # Common Cygwin-specific checks
    if "command not found" in result.stderr:
        print("Try: which some-command")
    elif "permission denied" in result.stderr:
        print("Try: chmod +x some-command")
```

## 🚀 Performance Optimization

### File Watching Performance
```python
# The connector automatically uses polling on Cygwin
# You can adjust polling interval if needed by modifying:
# PollingFileWatcher._poll_loop() sleep time
```

### Command Execution Performance
```bash
# Reduce startup overhead
export CYGWIN=nodosfilewarning

# Use efficient commands
run_command("find . -name '*.py' | wc -l")  # Fast
# vs
run_command("ls -R | grep '.py$' | wc -l")  # Slower
```

## 🆘 Getting Help

### Cygwin-Specific Resources
- **Cygwin FAQ**: https://cygwin.com/faq.html
- **Path conversion**: `man cygpath`
- **Package management**: `cygcheck -c` (list installed packages)

### Debugging Commands
```bash
# Check Cygwin installation
cygcheck -c python3

# Check Python modules
python -c "import sys; print('\n'.join(sys.path))"

# Check shell
echo $SHELL
which bash

# Check permissions
id
groups
```

### Log Analysis
```bash
# Enable debug logging
export CLAUDE_SHELL_LOG_LEVEL=DEBUG

# Check connector logs
tail -f claude_connector/connector.log
```

## 📚 Alternative Solutions

If Cygwin continues to cause issues:

### 1. Use WSL Instead
```bash
# Install WSL (Windows Subsystem for Linux)
wsl --install

# Use Claude Shell Connector in WSL
```

### 2. Use Git Bash
```bash
# Install Git for Windows
# Use Git Bash as shell instead of Cygwin bash
```

### 3. Use Native Windows Python
```powershell
# Use Windows Python with PowerShell
# Install dependencies normally
pip install -e .
```

---

**Remember**: Cygwin is a compatibility layer, so some limitations are expected. The connector is designed to gracefully handle these limitations while providing full functionality.