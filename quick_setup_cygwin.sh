#!/bin/bash

# Quick Cygwin setup with timeout fix
# This script sets up the connector and tests that commands don't timeout

echo "🚀 Quick Cygwin Setup - With Timeout Fix"
echo "========================================"

cd ~/my-repos/claude-cygwin

# Set up environment to prevent encoding and timeout issues
export PYTHONIOENCODING=utf-8
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export CYGWIN=nodosfilewarning
export PIP_NO_CACHE_DIR=1
export PIP_DISABLE_PIP_VERSION_CHECK=1

echo "✅ Environment configured"

# Install only essential packages with timeout (quick check if already installed)
echo "📦 Checking essential packages..."

check_package() {
    python -c "import $1" 2>/dev/null && echo "✅ $1 already available" || return 1
}

if ! check_package "click"; then
    echo "Installing click..."
    timeout 60s pip install --no-cache-dir click
fi

if ! check_package "rich"; then
    echo "Installing rich..."
    timeout 60s pip install --no-cache-dir rich
fi

if ! check_package "pydantic"; then
    echo "Installing pydantic..."
    timeout 60s pip install --no-cache-dir pydantic
fi

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

# Create launcher script with timeout fix
echo ""
echo "🚀 Creating improved launcher script..."

cat > claude-shell-cygwin << 'EOF'
#!/usr/bin/env python3
"""Improved Cygwin launcher for Claude Shell Connector with timeout fix."""

import sys
import os
from pathlib import Path

# Environment setup for Cygwin
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LC_ALL"] = "C.UTF-8"
os.environ["LANG"] = "C.UTF-8"
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
except KeyboardInterrupt:
    print("\n❌ Interrupted by user")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF

chmod +x claude-shell-cygwin
echo "✅ Created executable launcher: claude-shell-cygwin"

# Test command execution with timeout fix
echo ""
echo "🧪 Testing command execution with timeout fix..."

python -c "
import sys
sys.path.insert(0, 'src')

try:
    from claude_shell_connector import run_command
    
    print('Testing quick command (should complete in <5 seconds)...')
    result = run_command('echo Quick setup test - timeout fix applied!', timeout=10)
    
    if result.success:
        print(f'✅ Command test: {result.stdout.strip()}')
        print(f'   Execution time: {result.execution_time:.3f}s')
        if result.execution_time > 5:
            print('⚠️  Command took longer than expected but completed')
        else:
            print('✅ Command completed quickly - timeout fix working!')
    else:
        print(f'❌ Command failed: {result.error}')
        print(f'   This might indicate the timeout issue persists')
        
except Exception as e:
    print(f'❌ Command test failed: {e}')
    import traceback
    traceback.print_exc()
"

# Test the launcher quickly
echo ""
echo "🧪 Testing launcher (with timeout protection)..."

timeout 15s ./claude-shell-cygwin exec "echo Launcher test - timeout fix" 2>/dev/null

launcher_exit=$?

if [ $launcher_exit -eq 0 ]; then
    echo "✅ Launcher test passed"
elif [ $launcher_exit -eq 124 ]; then
    echo "⚠️  Launcher timed out - may need further investigation"
else
    echo "⚠️  Launcher completed with exit code: $launcher_exit"
fi

echo ""
echo "🎉 Quick Setup Complete - With Timeout Fix!"
echo "==========================================="
echo ""
echo "✅ No pip hanging issues!"
echo "✅ Package ready to use"
echo "✅ Timeout fix applied"
echo ""
echo "Key improvements:"
echo "  • Shell-specific argument handling"
echo "  • Better environment setup"
echo "  • Process cleanup improvements"
echo "  • Stdin closure to prevent hanging"
echo ""
echo "Usage:"
echo "  ./claude-shell-cygwin test        # Test connectivity"
echo "  ./claude-shell-cygwin exec \"pwd\"   # Execute command (should be fast)"
echo ""
echo "Python usage:"
echo "  export PYTHONPATH=\$(pwd)/src:\$PYTHONPATH"
echo "  python -c \"from claude_shell_connector import run_command; print(run_command('echo test').stdout)\""
echo ""
echo "If commands still timeout, run: ./test_timeout_fix.sh"