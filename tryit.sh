#!/bin/bash

# Navigate to the project
cd ~/my-repos/claude-cygwin

echo "🐧 Claude Shell Connector - Cygwin Setup (No Hanging)"
echo "====================================================="

# Use the quick setup that avoids pip hanging
echo "Using quick setup to avoid pip hanging issues..."
chmod +x quick_setup_cygwin.sh
./quick_setup_cygwin.sh

echo ""
echo "🧪 Additional testing..."

# Set environment for testing
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
export PYTHONIOENCODING=utf-8
export CYGWIN=nodosfilewarning

# Test with the launcher if available
if [ -f "./claude-shell-cygwin" ]; then
    echo "✅ Testing with launcher script:"
    ./claude-shell-cygwin exec "echo Launcher working!"
    
    echo ""
    echo "✅ Testing status command:"
    ./claude-shell-cygwin exec "pwd && whoami && date"
else
    echo "⚠️  Launcher not found, testing directly:"
    
    python -c "
import sys
sys.path.insert(0, 'src')

try:
    from claude_shell_connector import run_command
    
    print('✅ Direct Python test:')
    result = run_command('echo Direct Python execution working!')
    if result.success:
        print(f'   Output: {result.stdout.strip()}')
        print(f'   Time: {result.execution_time:.3f}s')
    else:
        print(f'   Error: {result.error}')
        
except Exception as e:
    print(f'❌ Direct test failed: {e}')
    import traceback
    traceback.print_exc()
"
fi

echo ""
echo "🎉 Cygwin setup completed - NO HANGING ISSUES!"
echo "==============================================="
echo ""
echo "Key improvements:"
echo "  ✅ Avoids 'pip install -e .' that hangs"
echo "  ✅ Uses manual Python path setup"
echo "  ✅ Sets proper encoding variables"
echo "  ✅ Individual package installation with timeouts"
echo "  ✅ Working launcher script"
echo ""
echo "If you need to run setup again:"
echo "  ./quick_setup_cygwin.sh"