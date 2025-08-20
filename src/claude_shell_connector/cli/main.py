"""Command line interface for Claude Shell Connector."""

import json
import sys
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .. import __version__
from ..config.settings import ConnectorConfig
from ..core.connector import ShellConnector
from ..core.exceptions import ClaudeShellConnectorError
from ..helpers.shell import run_command, format_result, get_connector_status

console = Console()


@click.group()
@click.version_option(version=__version__)
def main():
    """Claude Shell Connector - Bridge between Claude Desktop and shell environments."""
    pass


@main.command()
@click.option("--work-dir", "-w", help="Working directory for communication files")
@click.option("--shell-path", "-s", help="Path to shell executable")
@click.option("--timeout", "-t", type=int, default=30, help="Default timeout in seconds")
def start(work_dir: Optional[str], shell_path: Optional[str], timeout: int):
    """Start the connector service."""
    try:
        config = ConnectorConfig()
        if work_dir:
            config.work_dir = work_dir
        if shell_path:
            config.shell_path = Path(shell_path)
        config.default_timeout = timeout
        
        if not config.shell_path.exists():
            console.print(f"❌ [red]Shell not found at: {config.shell_path}[/red]")
            sys.exit(1)
        
        connector = ShellConnector(config)
        
        console.print("🚀 [green]Starting connector...[/green]")
        connector.start()
        
        console.print(f"✅ [green]Connector started![/green]")
        console.print(f"📁 Work directory: {config.work_dir}")
        console.print(f"🐚 Shell: {config.shell_path}")
        console.print(f"⏱️ Default timeout: {timeout}s")
        console.print("\n💡 [dim]Press Ctrl+C to stop[/dim]")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n🛑 [yellow]Stopping connector...[/yellow]")
            connector.stop()
            console.print("✅ [green]Stopped![/green]")
            
    except ClaudeShellConnectorError as e:
        console.print(f"❌ [red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option("--work-dir", "-w", help="Working directory for communication files")
def status(work_dir: Optional[str]):
    """Check connector status."""
    status_data = get_connector_status(work_dir)
    
    table = Table(title="Connector Status", show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    
    status_color = {
        "ready": "green",
        "executing": "yellow",
        "error": "red",
        "stopped": "red",
        "not_running": "red",
    }.get(status_data.get("status", "unknown"), "white")
    
    table.add_row("Status", f"[{status_color}]{status_data.get('status', 'unknown').upper()}[/]")
    table.add_row("Message", status_data.get("message", ""))
    
    if "work_dir" in status_data:
        table.add_row("Work Directory", status_data["work_dir"])
    if "shell_path" in status_data:
        table.add_row("Shell Path", status_data["shell_path"])
    if "commands_executed" in status_data:
        table.add_row("Commands Executed", str(status_data["commands_executed"]))
    if "uptime" in status_data:
        table.add_row("Uptime", f"{status_data['uptime']:.1f} seconds")
    
    console.print(table)


@main.command()
@click.argument("command")
@click.option("--work-dir", "-w", help="Working directory for communication files")
@click.option("--timeout", "-t", type=int, default=30, help="Command timeout")
@click.option("--working-dir", "-C", help="Working directory for command execution")
def exec(command: str, work_dir: Optional[str], timeout: int, working_dir: Optional[str]):
    """Execute a command."""
    console.print(f"🚀 [blue]Executing:[/blue] {command}")
    
    result = run_command(
        command=command,
        working_dir=working_dir,
        timeout=timeout,
        work_dir=work_dir,
    )
    
    console.print(format_result(result))


@main.command()
@click.option("--shell-path", "-s", help="Shell path to test")
def test(shell_path: Optional[str]):
    """Test shell connectivity."""
    try:
        config = ConnectorConfig()
        if shell_path:
            config.shell_path = Path(shell_path)
        
        console.print("🧪 [blue]Testing shell connectivity...[/blue]")
        
        if not config.shell_path.exists():
            console.print(f"❌ [red]Shell not found at: {config.shell_path}[/red]")
            return
        
        console.print(f"✅ Shell found at: {config.shell_path}")
        
        # Test basic commands
        test_commands = [
            "echo 'Hello from Claude Shell Connector!'",
            "pwd",
            "whoami",
        ]
        
        connector = ShellConnector(config)
        
        for cmd in test_commands:
            console.print(f"\nTesting: {cmd}")
            result = connector.execute_command(cmd, timeout=10)
            
            if result.success:
                console.print(f"✅ Success: {result.stdout.strip()}")
            else:
                console.print(f"❌ Failed: {result.error or 'Unknown error'}")
        
        console.print("\n🎉 [green]Testing completed![/green]")
        
    except Exception as e:
        console.print(f"❌ [red]Test failed: {e}[/red]")


if __name__ == "__main__":
    main()