"""Advanced usage examples for Claude Shell Connector."""

import json
import time
from pathlib import Path

from claude_shell_connector import ShellConnector, run_command, run_commands
from claude_shell_connector.config import ConnectorConfig
from claude_shell_connector.helpers.shell import format_result, get_connector_status


def example_1_quick_commands():
    """Example 1: Quick command execution."""
    print("=" * 50)
    print("Example 1: Quick Command Execution")
    print("=" * 50)
    
    # Simple command
    result = run_command("echo 'Hello from Claude Shell Connector!'")
    print("Simple echo command:")
    print(format_result(result))
    
    # Command with timeout
    result = run_command("sleep 2 && echo 'Done waiting'", timeout=5)
    print("\nCommand with timeout:")
    print(format_result(result))
    
    # Multiple commands
    commands = [
        "pwd",
        "whoami", 
        "date",
        "echo 'Current directory contents:' && ls -la"
    ]
    
    print(f"\nExecuting {len(commands)} commands:")
    results = run_commands(commands, stop_on_error=False)
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Command {i}: {commands[i-1]} ---")
        print(f"Success: {result.success}")
        if result.stdout:
            print(f"Output: {result.stdout.strip()}")


def example_2_connector_service():
    """Example 2: Using connector as a service."""
    print("\n" + "=" * 50)
    print("Example 2: Connector Service")
    print("=" * 50)
    
    # Custom configuration
    config = ConnectorConfig()
    config.default_timeout = 60
    
    print(f"Shell: {config.shell_path}")
    print(f"Work directory: {config.work_dir}")
    
    # Use connector as context manager
    with ShellConnector(config) as connector:
        print(f"Connector status: {connector.is_running()}")
        
        # Execute development workflow
        workflow_commands = [
            "echo 'Starting development workflow...'",
            "echo 'Checking Python version:' && python --version",
            "echo 'Checking pip version:' && pip --version",
            "echo 'Current working directory:' && pwd",
            "echo 'Available space:' && df -h . | head -2",
        ]
        
        for cmd in workflow_commands:
            print(f"\n🔧 Executing: {cmd}")
            result = connector.execute_command(cmd, timeout=10)
            
            if result.success:
                print(f"✅ {result.stdout.strip()}")
            else:
                print(f"❌ Error: {result.error}")
                print(f"   Exit code: {result.exit_code}")


def example_3_file_operations():
    """Example 3: File operations and project management."""
    print("\n" + "=" * 50)
    print("Example 3: File Operations")
    print("=" * 50)
    
    # Create a temporary workspace
    workspace = Path("./temp_workspace")
    
    try:
        # Setup commands
        setup_commands = [
            f"mkdir -p {workspace}",
            f"cd {workspace} && echo 'Hello World' > hello.txt",
            f"cd {workspace} && echo 'print(\"Hello from Python!\")' > hello.py",
            f"cd {workspace} && ls -la",
        ]
        
        print("Setting up temporary workspace...")
        results = run_commands(setup_commands)
        
        # File analysis commands
        analysis_commands = [
            f"find {workspace} -type f -name '*.txt' -exec wc -l {{}} +",
            f"find {workspace} -type f -name '*.py' -exec python {{}} \\;",
            f"cd {workspace} && file *",
            f"cd {workspace} && du -sh *",
        ]
        
        print("\nAnalyzing files...")
        for cmd in analysis_commands:
            result = run_command(cmd, timeout=15)
            print(f"\n💾 {cmd}")
            if result.success and result.stdout.strip():
                print(f"   {result.stdout.strip()}")
        
    finally:
        # Cleanup
        cleanup_result = run_command(f"rm -rf {workspace}")
        if cleanup_result.success:
            print(f"\n🧹 Cleaned up workspace: {workspace}")


def example_4_development_workflow():
    """Example 4: Development workflow automation."""
    print("\n" + "=" * 50)
    print("Example 4: Development Workflow")
    print("=" * 50)
    
    # Simulate a development project check
    project_commands = {
        "Git Status": "git status --porcelain",
        "Python Files": "find . -name '*.py' | wc -l", 
        "Test Files": "find . -name 'test_*.py' | wc -l",
        "Requirements": "[ -f requirements.txt ] && echo 'Found' || echo 'Missing'",
        "Virtual Env": "[ -d venv ] && echo 'Found' || echo 'Missing'",
    }
    
    project_info = {}
    
    for check_name, command in project_commands.items():
        result = run_command(command, timeout=10)
        
        if result.success:
            project_info[check_name] = result.stdout.strip()
            print(f"✅ {check_name}: {result.stdout.strip()}")
        else:
            project_info[check_name] = "Error"
            print(f"❌ {check_name}: Failed")
    
    # Generate project summary
    print(f"\n📊 Project Summary:")
    print(json.dumps(project_info, indent=2))


def example_5_error_handling():
    """Example 5: Error handling and recovery."""
    print("\n" + "=" * 50) 
    print("Example 5: Error Handling")
    print("=" * 50)
    
    # Test various error conditions
    error_tests = [
        ("Valid command", "echo 'This should work'"),
        ("Invalid command", "nonexistent_command_12345"),
        ("Timeout test", "sleep 10"),  # Will timeout with default 30s
        ("Permission test", "cat /etc/shadow 2>/dev/null || echo 'Permission denied'"),
        ("Path test", "cd /nonexistent/path 2>/dev/null || echo 'Path not found'"),
    ]
    
    for test_name, command in error_tests:
        print(f"\n🧪 Testing: {test_name}")
        print(f"   Command: {command}")
        
        # Use short timeout for timeout test
        timeout = 3 if "sleep" in command else 10
        
        result = run_command(command, timeout=timeout)
        
        print(f"   Success: {result.success}")
        print(f"   Exit code: {result.exit_code}")
        
        if result.success and result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        
        if not result.success:
            if result.error:
                print(f"   Error: {result.error}")
            if result.stderr:
                print(f"   Stderr: {result.stderr.strip()}")


def example_6_connector_status():
    """Example 6: Monitoring connector status."""
    print("\n" + "=" * 50)
    print("Example 6: Connector Status Monitoring")
    print("=" * 50)
    
    # Check if connector is running
    status = get_connector_status()
    print("Current connector status:")
    print(json.dumps(status, indent=2))
    
    if status.get("status") == "not_running":
        print("\n🚀 Starting temporary connector for demo...")
        
        config = ConnectorConfig()
        connector = ShellConnector(config)
        
        try:
            connector.start()
            
            # Execute a few commands to generate activity
            for i in range(3):
                result = connector.execute_command(f"echo 'Test command {i+1}'")
                print(f"   Command {i+1}: {'✅' if result.success else '❌'}")
                time.sleep(0.5)
            
            # Check status again
            final_status = connector.get_status()
            print(f"\nFinal connector statistics:")
            print(f"   Commands executed: {final_status.commands_executed}")
            print(f"   Uptime: {final_status.uptime:.1f} seconds")
            print(f"   Status: {final_status.status}")
            
        finally:
            connector.stop()
            print("🛑 Connector stopped")
    else:
        print("✅ Connector is already running externally")


def main():
    """Run all examples."""
    print("Claude Shell Connector - Advanced Examples")
    print("=" * 60)
    
    try:
        example_1_quick_commands()
        example_2_connector_service()
        example_3_file_operations()
        example_4_development_workflow()
        example_5_error_handling()
        example_6_connector_status()
        
        print("\n" + "=" * 60)
        print("🎉 All examples completed successfully!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n❌ Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()