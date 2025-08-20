#!/usr/bin/env python3
"""
Deep diagnostic to identify the real cause of persistent timeout issues.
"""

import os
import subprocess
import sys
import time
import signal
from pathlib import Path

# Add source to path
sys.path.insert(0, 'src')

def test_shell_variants():
    """Test different shell execution methods to find what works."""
    print("🔍 Testing shell execution variants...")
    
    shells_and_methods = [
        ("/bin/bash", ["-c"]),
        ("/bin/bash", ["-l", "-c"]),
        ("/usr/bin/bash", ["-c"]),  
        ("/bin/alt-bash", ["-c"]),
        ("/bin/alt-bash", ["-l", "-c"]),
        ("/bin/sh", ["-c"]),
    ]
    
    test_command = "echo 'Hello from shell test'"
    
    for shell_path, args in shells_and_methods:
        shell = Path(shell_path)
        if not shell.exists():
            print(f"❌ {shell_path} - not found")
            continue
            
        print(f"\n🧪 Testing: {shell_path} {' '.join(args)}")
        
        try:
            start_time = time.time()
            
            # Test with minimal setup
            result = subprocess.run(
                [str(shell)] + args + [test_command],
                capture_output=True,
                text=True,
                timeout=5,  # Short timeout to identify hangs quickly
                env={"PATH": os.environ.get("PATH", "")},  # Minimal env
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Success: {result.stdout.strip()} ({execution_time:.3f}s)")
            else:
                print(f"❌ Failed (exit {result.returncode}): {result.stderr.strip()}")
                
        except subprocess.TimeoutExpired:
            print(f"❌ TIMEOUT (>5s) - shell hangs")
        except Exception as e:
            print(f"❌ Error: {e}")


def test_environment_impact():
    """Test how environment variables affect shell execution."""
    print("\n🔍 Testing environment variable impact...")
    
    shell_path = "/bin/alt-bash"  # The problematic shell
    if not Path(shell_path).exists():
        shell_path = "/bin/bash"
    
    test_command = "echo 'Environment test'"
    
    env_variants = [
        ("Minimal", {"PATH": os.environ.get("PATH", "")}),
        ("Standard", os.environ.copy()),
        ("Cygwin-specific", {
            **os.environ,
            "CYGWIN": "nodosfilewarning",
            "PYTHONIOENCODING": "utf-8",
            "LC_ALL": "C.UTF-8",
        }),
        ("No-environment", {}),
    ]
    
    for env_name, env in env_variants:
        print(f"\n🧪 Testing with {env_name} environment:")
        
        try:
            start_time = time.time()
            
            result = subprocess.run(
                [shell_path, "-c", test_command],
                capture_output=True,
                text=True,
                timeout=5,
                env=env,
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Success: {result.stdout.strip()} ({execution_time:.3f}s)")
            else:
                print(f"❌ Failed: {result.stderr.strip()}")
                
        except subprocess.TimeoutExpired:
            print(f"❌ TIMEOUT - hangs with {env_name} environment")
        except Exception as e:
            print(f"❌ Error: {e}")


def test_connector_internals():
    """Test the connector's internal command execution."""
    print("\n🔍 Testing connector internals...")
    
    try:
        from claude_shell_connector.core.connector import ShellConnector
        from claude_shell_connector.config.settings import ConnectorConfig
        
        # Test with debug logging
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        config = ConnectorConfig()
        print(f"Config shell: {config.shell_path}")
        print(f"Config timeout: {config.default_timeout}")
        
        connector = ShellConnector(config)
        print(f"Connector shell type: {getattr(connector, 'shell_type', 'unknown')}")
        print(f"Connector shell args: {getattr(connector, 'shell_args', 'unknown')}")
        
        # Test direct execution without starting service
        print("\n🧪 Testing direct execution...")
        connector._running = True  # Bypass the running check
        
        start_time = time.time()
        result = connector.execute_command("echo 'Direct test'", timeout=5)
        execution_time = time.time() - start_time
        
        print(f"Result success: {result.success}")
        print(f"Result stdout: {result.stdout}")
        print(f"Result stderr: {result.stderr}")
        print(f"Result error: {result.error}")
        print(f"Execution time: {execution_time:.3f}s")
        
    except Exception as e:
        print(f"❌ Connector test failed: {e}")
        import traceback
        traceback.print_exc()


def test_process_behavior():
    """Test subprocess behavior patterns."""
    print("\n🔍 Testing subprocess behavior patterns...")
    
    shell_path = "/bin/alt-bash"
    if not Path(shell_path).exists():
        shell_path = "/bin/bash"
    
    test_scenarios = [
        ("Basic", {"stdin": subprocess.PIPE}),
        ("No stdin", {"stdin": subprocess.DEVNULL}),
        ("Closed stdin", {"stdin": subprocess.PIPE, "close_stdin": True}),
        ("No env", {"env": {}}),
        ("Detached", {"start_new_session": True}),
    ]
    
    for scenario_name, kwargs in test_scenarios:
        print(f"\n🧪 Testing {scenario_name} scenario:")
        
        try:
            start_time = time.time()
            
            close_stdin = kwargs.pop("close_stdin", False)
            
            process = subprocess.Popen(
                [shell_path, "-c", "echo 'Process test'"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                **kwargs
            )
            
            if close_stdin and process.stdin:
                process.stdin.close()
            
            stdout, stderr = process.communicate(timeout=5)
            execution_time = time.time() - start_time
            
            if process.returncode == 0:
                print(f"✅ Success: {stdout.strip()} ({execution_time:.3f}s)")
            else:
                print(f"❌ Failed: {stderr.strip()}")
                
        except subprocess.TimeoutExpired:
            try:
                process.kill()
                process.wait()
            except:
                pass
            print(f"❌ TIMEOUT - {scenario_name} scenario hangs")
        except Exception as e:
            print(f"❌ Error: {e}")


def test_simple_workaround():
    """Test a simple workaround approach."""
    print("\n🔍 Testing simple workaround...")
    
    # Try using system() or os.popen() instead of subprocess
    try:
        print("🧪 Testing os.system():")
        start_time = time.time()
        result = os.system("echo 'OS system test' > /tmp/test_output.txt")
        execution_time = time.time() - start_time
        
        if result == 0:
            try:
                with open("/tmp/test_output.txt", "r") as f:
                    output = f.read().strip()
                print(f"✅ Success: {output} ({execution_time:.3f}s)")
                os.unlink("/tmp/test_output.txt")
            except:
                print(f"✅ Command executed ({execution_time:.3f}s)")
        else:
            print(f"❌ Failed with exit code: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    try:
        print("\n🧪 Testing os.popen():")
        start_time = time.time()
        with os.popen("echo 'OS popen test'") as pipe:
            output = pipe.read()
        execution_time = time.time() - start_time
        
        print(f"✅ Success: {output.strip()} ({execution_time:.3f}s)")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run comprehensive diagnostics."""
    print("🔍 Deep Diagnostic - Persistent Timeout Issue")
    print("=" * 50)
    
    # Set up minimal environment
    os.environ["PYTHONIOENCODING"] = "utf-8"
    
    test_shell_variants()
    test_environment_impact()
    test_process_behavior()
    test_simple_workaround()
    test_connector_internals()
    
    print("\n" + "=" * 50)
    print("🎯 Deep Diagnostic Summary:")
    print("Look for which method completes quickly (<1s)")
    print("vs which methods timeout (>5s)")
    print("This will identify the real root cause")


if __name__ == "__main__":
    main()