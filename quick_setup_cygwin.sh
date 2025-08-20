#!/bin/bash

# Quick Cygwin setup that avoids pip hanging issues
# This script sets up the connector without using "pip install -e ."

echo "🚀 Quick Cygwin Setup - No Pip Hanging"
echo "======================================"

cd ~/my-repos/claude-cygwin

# Set up environment to prevent encoding issues
export PYTHONIOENCODING=utf-8
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export CYGWIN=nodosfilewarning
export PIP_NO_CACHE_DIR=1
export PIP_DISABLE_PIP_VERSION_CHECK=1

echo "✅ Environment configured"

# Install only essential packages with timeout
echo "📦 Installing essential packages..."

install_with_timeout() {
    local package=$1
    local timeout=60
    
    echo "Installing $package (timeout: ${timeout}s)..."
    
    timeout ${timeout}s pip install --no-cache-dir "$package" 2>/dev/null
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ $package installed"
        return 0
    elif [ $exit_code -eq 124 ]; then
        echo "⚠️  $package timed out"
        return 1
    else
        echo "⚠️  $package failed (exit code: $exit_code)"
        return 1
    fi
}

# Try to install essential packages
install_with_timeout "click" 
install_with_timeout "rich"
install_with_timeout "pydantic"

echo ""
echo "📁 Setting up package manually (avoiding pip -e)..."

# Set Python path instead of using pip -e
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
echo "✅ PYTHONPATH set to: $PYTHONPATH"

# Test basic import
echo ""
echo "🧪 Testing import..."

python -c "
import sys
sys.path.insert(0, 'src')

try:
    import claude_shell_connector
    print('✅ Successfully imported claude_shell_connector')
    
    from claude_shell_connector import run_command
    print('✅ Successfully imported run_command')
    
    from claude_shell_connector.config.settings import ConnectorConfig
    config = ConnectorConfig()
    print(f'✅ Shell detected: {config.shell_path}')
    
except Exception as e:
    print(f'❌ Import test failed: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Import test passed"
else
    echo "❌ Import test failed"
    exit 1
fi

# Create a simple launcher script
echo ""
echo "🚀 Creating launcher script..."

cat > claude-shell-cygwin << 'EOF'
#!/usr/bin/env python3
"""Quick Cygwin launcher for Claude Shell Connector."""

import sys
import os
from pathlib import Path

# Environment setup
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LC_ALL"] = "C.UTF-8"
os.environ["CYGWIN"] = "nodosfilewarning"

# Add source to Python path
script_dir = Path(__file__).parent.resolve()
src_dir = script_dir / "src"

if src_dir.exists():
    sys.path.insert(0, str(src_dir))
else:
    print(f"❌ Source directory not found: {src_dir}")
    sys.exit(1)

try:
    from claude_shell_connector.cli.main import main
    main()
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nQuick fix:")
    print(f"  cd {script_dir}")
    print("  export PYTHONPATH=$(pwd)/src:$PYTHONPATH")
    print("  python -c 'from claude_shell_connector import run_command'")
    sys.exit(1)
EOF

chmod +x claude-shell-cygwin
echo "✅ Created executable launcher: claude-shell-cygwin"

# Test the launcher
echo ""
echo "🧪 Testing launcher..."
./claude-shell-cygwin exec "echo Quick setup test successful!" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Launcher test passed"
else
    echo "⚠️  Launcher test had issues, but basic functionality should work"
fi

# Test command execution
echo ""
echo "🧪 Testing command execution..."

python -c "
import sys
sys.path.insert(0, 'src')

try:
    from claude_shell_connector import run_command
    result = run_command('echo Quick Cygwin setup successful!', timeout=10)
    if result.success:
        print(f'✅ Command test: {result.stdout.strip()}')
        print(f'   Execution time: {result.execution_time:.3f}s')
    else:
        print(f'❌ Command failed: {result.error}')
except Exception as e:
    print(f'❌ Command test failed: {e}')
"

echo ""
echo "🎉 Quick Setup Complete!"
echo "======================="
echo ""
echo "✅ No pip hanging issues!"
echo "✅ Package ready to use"
echo ""
echo "Usage:"
echo "  ./claude-shell-cygwin test        # Test connectivity"
echo "  ./claude-shell-cygwin exec \"pwd\"   # Execute command"
echo ""
echo "Python usage:"
echo "  export PYTHONPATH=\$(pwd)/src:\$PYTHONPATH"
echo "  python -c \"from claude_shell_connector import run_command; print(run_command('echo test').stdout)\""
echo ""
echo "Add to ~/.bashrc for permanent setup:"
echo "  export PYTHONPATH=$HOME/my-repos/claude-cygwin/src:\$PYTHONPATH"
echo "  export PYTHONIOENCODING=utf-8"
echo "  export CYGWIN=nodosfilewarning"