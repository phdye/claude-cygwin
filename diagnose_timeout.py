#!/usr/bin/env python3
"""
Diagnostic script to identify the command execution timeout issue.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Add source to path
sys.path.insert(0, 'src')

def test_shell_directly():
    """Test shell execution directly without the connector."""
    print("🔍 Testing shell execution directly...")
    
    shells_to_test = [
        "/bin/bash",
        "/usr/bin/bash", 
        "/bin/alt-bash",
        "/bin/sh"
    ]
    
    for shell_path in shells_to_test:
        shell = Path(shell_path)
        if not shell.exists():
            print(f"❌ {shell_path} - not found")
            continue
            
        print(f"\n🧪 Testing {shell_path}...")
        
        # Test 1: Simple command without -l
        try:
            start_time = time.time()
            result = subprocess.run(
                [str(shell), "-c", "echo 'Hello from shell'"],
                capture_output=True,
                text=True,
                timeout=10,
                env=os.environ.copy()
            )
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Simple command: {result.stdout.strip()} ({execution_time:.3f}s)")
            else:
                print(f"❌ Simple command failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"❌ Simple command timed out")
        except Exception as e:
            print(f"❌ Simple command error: {e}")
        
        # Test 2: Command with -l (login shell)
        try:
            start_time = time.time()
            result = subprocess.run(
                [str(shell), "-l", "-c", "echo 'Hello from login shell'"],
                capture_output=True,
                text=True,
                timeout=10,
                env=os.environ.copy()
            )
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Login shell: {result.stdout.strip()} ({execution_time:.3f}s)")
            else:
                print(f"❌ Login shell failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"❌ Login shell timed out")
        except Exception as e:
            print(f"❌ Login shell error: {e}")


def test_connector_config():
    """Test connector configuration."""
    print("\n🔍 Testing connector configuration...")
    
    try:
        from claude_shell_connector.config.settings import ConnectorConfig
        
        config = ConnectorConfig()
        print(f"✅ Detected shell: {config.shell_path}")
        print(f"✅ Work directory: {config.work_dir}")
        print(f"✅ Default timeout: {config.default_timeout}")
        
        # Test if detected shell works
        shell_path = config.shell_path
        if shell_path.exists():
            print(f"✅ Shell exists: {shell_path}")
            
            # Quick test
            try:
                result = subprocess.run(
                    [str(shell_path), "-c", "echo 'Config test'"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    print(f"✅ Shell works: {result.stdout.strip()}")
                else:
                    print(f"❌ Shell test failed: {result.stderr}")
            except subprocess.TimeoutExpired:
                print(f"❌ Shell test timed out")
        else:
            print(f"❌ Detected shell doesn't exist: {shell_path}")
            
    except Exception as e:
        print(f"❌ Config test failed: {e}")


def test_environment():
    """Test environment variables."""
    print("\n🔍 Testing environment...")
    
    important_vars = [
        "SHELL", "PATH", "HOME", "USER", "TERM",
        "PYTHONPATH", "PYTHONIOENCODING", "LC_ALL", "LANG", "CYGWIN"
    ]
    
    for var in important_vars:
        value = os.environ.get(var, "NOT SET")
        print(f"  {var}: {value}")


def test_simple_connector():
    """Test the connector with minimal setup."""
    print("\n🔍 Testing simple connector execution...")
    
    try:
        from claude_shell_connector.core.connector import ShellConnector
        from claude_shell_connector.config.settings import ConnectorConfig
        
        # Create config with short timeout
        config = ConnectorConfig()
        config.default_timeout = 10
        
        print(f"Using shell: {config.shell_path}")
        
        connector = ShellConnector(config)
        
        try:
            print("Starting connector...")
            connector.start()
            print("✅ Connector started")
            
            print("Executing simple command...")
            result = connector.execute_command("echo 'Simple test'", timeout=5)
            
            if result.success:
                print(f"✅ Command succeeded: {result.stdout.strip()}")
                print(f"   Execution time: {result.execution_time:.3f}s")
            else:
                print(f"❌ Command failed: {result.error}")
                print(f"   Exit code: {result.exit_code}")
                print(f"   Stderr: {result.stderr}")
                
        finally:
            connector.stop()
            print("✅ Connector stopped")
            
    except Exception as e:
        print(f"❌ Connector test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all diagnostic tests."""
    print("🔍 Claude Shell Connector - Timeout Diagnostic")
    print("=" * 50)
    
    # Set up environment
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["LC_ALL"] = "C.UTF-8"
    os.environ["CYGWIN"] = "nodosfilewarning"
    
    test_environment()
    test_shell_directly()
    test_connector_config()
    test_simple_connector()
    
    print("\n" + "=" * 50)
    print("🎯 Diagnostic Summary:")
    print("If shells work directly but connector times out,")
    print("the issue is in the connector implementation.")
    print("If shells timeout directly, the issue is with")
    print("the shell configuration or environment.")


if __name__ == "__main__":
    main()