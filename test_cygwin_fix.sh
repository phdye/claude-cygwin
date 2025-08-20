#!/bin/bash

echo "🧪 Testing Cygwin Compatibility Fix"
echo "==================================="

cd ~/my-repos/claude-cygwin

# Test 1: Run the Cygwin setup
echo "Test 1: Running Cygwin setup..."
python setup_cygwin.py

echo ""
echo "Test 2: Testing Python import..."

# Test 2: Test import with PYTHONPATH
export PYTHONPATH=$(pwd)/src:$PYTHONPATH

python -c "
try:
    print('Attempting import...')
    import claude_shell_connector
    print('✅ Successfully imported claude_shell_connector')
    
    from claude_shell_connector import run_command
    print('✅ Successfully imported run_command')
    
    from claude_shell_connector.config.settings import ConnectorConfig
    config = ConnectorConfig()
    print(f'✅ Config created, shell: {config.shell_path}')
    
    print('✅ All imports successful!')
    
except Exception as e:
    print(f'❌ Import failed: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "Test 3: Testing basic command execution..."

python -c "
import sys
sys.path.insert(0, 'src')

try:
    from claude_shell_connector import run_command
    
    print('Testing basic command...')
    result = run_command('echo Hello from fixed Cygwin connector!')
    
    if result.success:
        print(f'✅ Command successful: {result.stdout.strip()}')
        print(f'   Execution time: {result.execution_time:.3f}s')
        print(f'   Exit code: {result.exit_code}')
    else:
        print(f'❌ Command failed: {result.error}')
        
except Exception as e:
    print(f'❌ Test failed: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "Test 4: Testing launcher script (if available)..."

if [ -f "./claude-shell-cygwin" ]; then
    echo "✅ Launcher script exists"
    ./claude-shell-cygwin exec "echo Launcher works!"
else
    echo "⚠️  Launcher script not found (run setup_cygwin.py first)"
fi

echo ""
echo "🎉 Cygwin compatibility test completed!"
echo "If you see ✅ marks above, the fix is working correctly."