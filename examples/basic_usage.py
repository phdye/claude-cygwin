"""Basic usage example for Claude Shell Connector."""

from claude_shell_connector import run_command, ShellConnector
from claude_shell_connector.config import ConnectorConfig


def main():
    """Demonstrate basic usage."""
    print("Claude Shell Connector - Basic Example")
    print("=" * 40)
    
    # Method 1: Quick command execution
    print("\n1. Quick command execution:")
    result = run_command("echo 'Hello from Claude Shell Connector!'")
    
    if result.success:
        print(f"✅ Success: {result.stdout.strip()}")
        print(f"   Execution time: {result.execution_time:.2f}s")
    else:
        print(f"❌ Failed: {result.error}")
    
    # Method 2: Using connector directly
    print("\n2. Using connector directly:")
    
    config = ConnectorConfig()
    print(f"   Shell: {config.shell_path}")
    print(f"   Work dir: {config.work_dir}")
    
    with ShellConnector(config) as connector:
        # Execute multiple commands
        commands = [
            "pwd",
            "echo 'Current user:' && whoami",
            "echo 'Current date:' && date"
        ]
        
        for cmd in commands:
            print(f"\n   Executing: {cmd}")
            result = connector.execute_command(cmd)
            
            if result.success:
                print(f"   ✅ Output: {result.stdout.strip()}")
            else:
                print(f"   ❌ Error: {result.error}")
    
    print("\n" + "=" * 40)
    print("Example completed!")


if __name__ == "__main__":
    main()