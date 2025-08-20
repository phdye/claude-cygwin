#!/usr/bin/env python3
"""
Test the direct execution approach to bypass timeout issues.
"""

import sys
import time

# Add source to path
sys.path.insert(0, 'src')

def test_direct_execution():
    """Test the new direct execution method."""
    print("🧪 Testing Direct Execution (Bypassing Connector)")
    print("=" * 50)
    
    try:
        from claude_shell_connector.helpers.shell import run_command_direct, run_command_fallback
        
        # Test 1: Direct execution
        print("\n🧪 Test 1: Direct execution method")
        start_time = time.time()
        result = run_command_direct("echo 'Direct execution test'", timeout=5)
        test_time = time.time() - start_time
        
        print(f"Test execution time: {test_time:.3f}s")
        if result.success:
            print(f"✅ Success: {result.stdout.strip()}")
            print(f"   Command execution time: {result.execution_time:.3f}s")
        else:
            print(f"❌ Failed: {result.error}")
        
        # Test 2: Fallback method
        print("\n🧪 Test 2: Fallback execution method")
        start_time = time.time()
        result = run_command_fallback("echo 'Fallback execution test'", timeout=5)
        test_time = time.time() - start_time
        
        print(f"Test execution time: {test_time:.3f}s")
        if result.success:
            print(f"✅ Success: {result.stdout.strip()}")
            print(f"   Command execution time: {result.execution_time:.3f}s")
        else:
            print(f"❌ Failed: {result.error}")
        
        # Test 3: Main run_command function
        print("\n🧪 Test 3: Updated run_command function")
        start_time = time.time()
        
        from claude_shell_connector import run_command
        result = run_command("echo 'Updated run_command test'", timeout=5)
        test_time = time.time() - start_time
        
        print(f"Test execution time: {test_time:.3f}s")
        if result.success:
            print(f"✅ Success: {result.stdout.strip()}")
            print(f"   Command execution time: {result.execution_time:.3f}s")
        else:
            print(f"❌ Failed: {result.error}")
        
        # Test 4: Multiple commands
        print("\n🧪 Test 4: Multiple commands")
        start_time = time.time()
        
        test_commands = [
            "echo 'Command 1'",
            "pwd",
            "whoami",
            "date"
        ]
        
        from claude_shell_connector import run_commands
        results = run_commands(test_commands, timeout=5)
        test_time = time.time() - start_time
        
        print(f"Total test time: {test_time:.3f}s")
        
        success_count = sum(1 for r in results if r.success)
        print(f"✅ {success_count}/{len(results)} commands succeeded")
        
        for i, result in enumerate(results):
            if result.success:
                print(f"   {i+1}. {result.stdout.strip()} ({result.execution_time:.3f}s)")
            else:
                print(f"   {i+1}. Failed: {result.error}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


def test_shell_detection():
    """Test shell detection and availability."""
    print("\n🔍 Testing Shell Detection")
    print("=" * 30)
    
    from pathlib import Path
    
    shells_to_check = [
        "/bin/bash",
        "/usr/bin/bash",
        "/bin/alt-bash", 
        "/bin/sh"
    ]
    
    for shell in shells_to_check:
        if Path(shell).exists():
            print(f"✅ Found: {shell}")
            
            # Quick test
            import subprocess
            try:
                result = subprocess.run(
                    [shell, "-c", "echo 'Shell test'"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    stdin=subprocess.DEVNULL
                )
                
                if result.returncode == 0:
                    print(f"   ✅ Works: {result.stdout.strip()}")
                else:
                    print(f"   ❌ Fails: {result.stderr.strip()}")
                    
            except subprocess.TimeoutExpired:
                print(f"   ❌ Hangs")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        else:
            print(f"❌ Missing: {shell}")


def main():
    """Run all tests."""
    print("🚀 Direct Execution Test - Timeout Fix Verification")
    print("=" * 60)
    
    test_shell_detection()
    test_direct_execution()
    
    print("\n" + "=" * 60)
    print("🎯 Summary:")
    print("If commands execute quickly (<1s), the direct approach works!")
    print("If they still timeout, we need to investigate shell issues.")


if __name__ == "__main__":
    main()