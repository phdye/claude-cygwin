#!/bin/bash

echo "🧪 Testing Fix for Command Timeout Issue (004.txt)"
echo "================================================="

cd ~/my-repos/claude-cygwin

# Set environment
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
export PYTHONIOENCODING=utf-8
export LC_ALL=C.UTF-8
export CYGWIN=nodosfilewarning

echo "🔍 Running diagnostic first..."
python diagnose_timeout.py

echo ""
echo "🧪 Testing fixed connector..."

python -c "
import sys
sys.path.insert(0, 'src')

try:
    from claude_shell_connector import run_command
    
    print('🧪 Test 1: Simple echo command')
    result = run_command('echo Test 1: Simple command', timeout=10)
    if result.success:
        print(f'✅ Success: {result.stdout.strip()}')
        print(f'   Execution time: {result.execution_time:.3f}s')
    else:
        print(f'❌ Failed: {result.error}')
        
    print('')
    print('🧪 Test 2: Multiple commands')
    result = run_command('pwd && whoami && echo done', timeout=10)
    if result.success:
        print(f'✅ Success: {result.stdout.strip()}')
        print(f'   Execution time: {result.execution_time:.3f}s')
    else:
        print(f'❌ Failed: {result.error}')
        
    print('')
    print('🧪 Test 3: Date command')
    result = run_command('date', timeout=10)
    if result.success:
        print(f'✅ Success: {result.stdout.strip()}')
        print(f'   Execution time: {result.execution_time:.3f}s')
    else:
        print(f'❌ Failed: {result.error}')
        
    print('')
    print('🧪 Test 4: File listing')
    result = run_command('ls -la | head -5', timeout=10)
    if result.success:
        print(f'✅ Success: Command completed')
        print(f'   Lines of output: {len(result.stdout.splitlines())}')
        print(f'   Execution time: {result.execution_time:.3f}s')
    else:
        print(f'❌ Failed: {result.error}')
        
except Exception as e:
    print(f'❌ Test failed with exception: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "🧪 Testing launcher script..."

if [ -f "./claude-shell-cygwin" ]; then
    echo "Testing launcher with timeout protection..."
    
    timeout 15s ./claude-shell-cygwin exec "echo Launcher test - should not timeout"
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ Launcher test passed"
    elif [ $exit_code -eq 124 ]; then
        echo "❌ Launcher still timing out"
    else
        echo "⚠️  Launcher completed with exit code: $exit_code"
    fi
else
    echo "⚠️  Launcher script not found"
fi

echo ""
echo "📊 Test Summary:"
echo "================"
echo "If tests show execution times under 5 seconds, the fix is working."
echo "If commands still timeout after 10+ seconds, more investigation needed."
echo ""
echo "Key fixes applied:"
echo "  • Shell-specific argument handling"
echo "  • Improved environment setup"
echo "  • Better process cleanup"
echo "  • Stdin closure to prevent hanging"
echo "  • Process group management"