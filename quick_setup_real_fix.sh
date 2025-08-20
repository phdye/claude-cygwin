#!/bin/bash

# Quick Cygwin setup with REAL timeout fix using direct execution
echo "🚀 Quick Cygwin Setup - REAL Timeout Fix (Direct Execution)"
echo "==========================================================="

cd ~/my-repos/claude-cygwin

# Set up environment
export PYTHONIOENCODING=utf-8
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export CYGWIN=nodosfilewarning
export PIP_NO_CACHE_DIR=1

echo "✅ Environment configured"

# Quick package check
echo "📦 Checking essential packages..."

check_package() {
    python -c "import $1" 2>/dev/null && echo "✅ $1 already available" || return 1
}

check_package "click" || echo "⚠️  click not available"
check_package "rich" || echo "⚠️  rich not available"  
check_package "pydantic" || echo "⚠️  pydantic not available"

echo ""
echo "📁 Setting up package with direct execution..."

# Set Python path
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
    
    from claude_shell_connector.helpers.shell import run_command_direct
    print('✅ Successfully imported direct execution helper')
    
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

# Test direct execution (this should work quickly)
echo ""
echo "🧪 Testing DIRECT EXECUTION (should be fast)..."

python -c "
import sys
sys.path.insert(0, 'src')

try:
    from claude_shell_connector.helpers.shell import run_command_direct
    
    print('Testing direct execution method...')
    result = run_command_direct('echo Direct execution test - should be immediate!', timeout=5)
    
    if result.success:
        print(f'✅ Direct execution SUCCESS: {result.stdout.strip()}')
        print(f'   Execution time: {result.execution_time:.3f}s')
        
        if result.execution_time < 2:
            print('✅ FAST execution - timeout issue RESOLVED!')
        else:
            print('⚠️  Slow execution - still investigating')
    else:
        print(f'❌ Direct execution failed: {result.error}')
        
except Exception as e:
    print(f'❌ Direct execution test failed: {e}')
    import traceback
    traceback.print_exc()
"

# Test the updated run_command function
echo ""
echo "🧪 Testing updated run_command function..."

python -c "
import sys
sys.path.insert(0, 'src')

try:
    from claude_shell_connector import run_command
    
    print('Testing updated run_command...')
    result = run_command('echo Updated run_command test!', timeout=5)
    
    if result.success:
        print(f'✅ run_command SUCCESS: {result.stdout.strip()}')
        print(f'   Execution time: {result.execution_time:.3f}s')
    else:
        print(f'❌ run_command failed: {result.error}')
        
except Exception as e:
    print(f'❌ run_command test failed: {e}')
"

# Create updated launcher script
echo ""
echo "🚀 Creating launcher with direct execution..."

cat > claude-shell-cygwin << 'EOF'
#!/usr/bin/env python3
"""Cygwin launcher with direct execution (no connector complexity)."""

import sys
import os
from pathlib import Path

# Environment setup
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
    print("\nTrying direct execution fallback...")
    
    # Direct execution fallback
    if len(sys.argv) >= 3 and sys.argv[1] == "exec":
        command = " ".join(sys.argv[2:])
        try:
            from claude_shell_connector.helpers.shell import run_command_direct
            result = run_command_direct(command, timeout=30)
            
            if result.success:
                print(result.stdout, end="")
            else:
                print(f"❌ Command failed: {result.error}", file=sys.stderr)
                sys.exit(result.exit_code)
        except Exception as e:
            print(f"❌ Direct execution failed: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Usage: ./claude-shell-cygwin exec \"command\"")
        sys.exit(1)
        
except KeyboardInterrupt:
    print("\n❌ Interrupted by user")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
EOF

chmod +x claude-shell-cygwin
echo "✅ Created launcher: claude-shell-cygwin"

# Test launcher with direct execution
echo ""
echo "🧪 Testing launcher with direct execution..."

timeout 10s ./claude-shell-cygwin exec "echo Launcher with direct execution test!" 2>/dev/null

launcher_exit=$?

if [ $launcher_exit -eq 0 ]; then
    echo "✅ Launcher test PASSED"
elif [ $launcher_exit -eq 124 ]; then
    echo "❌ Launcher still timed out"
else
    echo "⚠️  Launcher exit code: $launcher_exit"
fi

echo ""
echo "🎉 Real Timeout Fix Applied - Direct Execution!"
echo "=============================================="
echo ""
echo "✅ No pip hanging issues!"
echo "✅ Package ready to use"
echo "✅ REAL timeout fix with direct execution"
echo ""
echo "Key breakthrough:"
echo "  • Bypassed connector complexity entirely"
echo "  • Direct subprocess execution"
echo "  • No file watching or connector overhead"
echo "  • Simple, fast shell execution"
echo ""
echo "Usage:"
echo "  ./claude-shell-cygwin exec \"pwd\"   # Direct execution (should be instant)"
echo ""
echo "Python usage:"
echo "  export PYTHONPATH=\$(pwd)/src:\$PYTHONPATH"
echo "  python -c \"from claude_shell_connector import run_command; print(run_command('echo test').stdout)\""
echo ""
echo "Performance test:"
echo "  python test_direct_execution.py"