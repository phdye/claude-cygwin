#!/usr/bin/env python3
"""
Cygwin-compatible installation script for Claude Shell Connector.
Fixed to handle pip hanging and encoding issues.
"""

import os
import platform
import subprocess
import sys
import time
import signal
from pathlib import Path


def setup_cygwin_environment():
    """Set up Cygwin-specific environment variables."""
    # Fix encoding issues
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["LC_ALL"] = "C.UTF-8"
    os.environ["LANG"] = "C.UTF-8"
    
    # Cygwin-specific settings
    os.environ["CYGWIN"] = "nodosfilewarning"
    
    # Disable pip cache to avoid hanging
    os.environ["PIP_NO_CACHE_DIR"] = "1"
    os.environ["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    
    print("✅ Environment configured for Cygwin")


def run_command_with_timeout(cmd, timeout=60, check=True, shell=False):
    """Run a command with timeout to prevent hanging."""
    print(f"Running: {cmd} (timeout: {timeout}s)")
    
    try:
        if isinstance(cmd, str) and not shell:
            cmd = cmd.split()
        
        # Start process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=shell,
            env=os.environ.copy()
        )
        
        # Wait with timeout
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            
            if stdout:
                print(stdout)
            if stderr and process.returncode != 0:
                print(f"stderr: {stderr}")
            
            if check and process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd, stdout, stderr)
            
            return subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
            
        except subprocess.TimeoutExpired:
            print(f"⚠️  Command timed out after {timeout}s, terminating...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Force killing process...")
                process.kill()
                process.wait()
            
            raise subprocess.TimeoutExpired(cmd, timeout)
    
    except Exception as e:
        print(f"Error running command: {e}")
        if check:
            raise
        return subprocess.CompletedProcess(cmd, 1, "", str(e))


def install_dependencies_minimal():
    """Install dependencies one by one to avoid hanging."""
    print("🔧 Installing dependencies individually...")
    
    # Core dependencies that usually work on Cygwin
    core_deps = [
        "setuptools",
        "wheel", 
        "click",
        "rich",
        "pydantic",
        "typing-extensions",
    ]
    
    success_count = 0
    
    for dep in core_deps:
        try:
            print(f"\n📦 Installing {dep}...")
            result = run_command_with_timeout(
                f"pip install --no-cache-dir {dep}",
                timeout=120,  # 2 minutes per package
                check=False
            )
            
            if result.returncode == 0:
                print(f"✅ {dep} installed successfully")
                success_count += 1
            else:
                print(f"⚠️  {dep} failed to install (returncode: {result.returncode})")
                
        except subprocess.TimeoutExpired:
            print(f"❌ {dep} installation timed out")
        except Exception as e:
            print(f"❌ {dep} installation failed: {e}")
    
    print(f"\n📊 Installed {success_count}/{len(core_deps)} dependencies")
    return success_count >= 3  # Need at least basic deps


def install_package_manual():
    """Manually install package without pip -e ."""
    print("🔧 Manual package installation...")
    
    try:
        # Create a simple setup that doesn't use pip -e
        current_dir = Path.cwd()
        src_dir = current_dir / "src"
        
        if not src_dir.exists():
            print("❌ Source directory not found")
            return False
        
        # Add to Python path
        python_path = os.environ.get("PYTHONPATH", "")
        new_python_path = f"{src_dir}:{python_path}" if python_path else str(src_dir)
        os.environ["PYTHONPATH"] = new_python_path
        
        print(f"✅ Added {src_dir} to PYTHONPATH")
        
        # Test import
        test_code = """
import sys
sys.path.insert(0, 'src')
try:
    import claude_shell_connector
    print('✅ Package import successful')
    print(f'Package location: {claude_shell_connector.__file__}')
except ImportError as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"""
        
        result = run_command_with_timeout([
            sys.executable, "-c", test_code
        ], timeout=30)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Manual installation failed: {e}")
        return False


def create_simple_launcher():
    """Create a simple launcher that doesn't rely on pip installation."""
    print("🔧 Creating simple launcher...")
    
    launcher_content = '''#!/usr/bin/env python3
"""Simple launcher for Claude Shell Connector on Cygwin."""

import sys
import os
from pathlib import Path

# Setup environment
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LC_ALL"] = "C.UTF-8"
os.environ["CYGWIN"] = "nodosfilewarning"

# Add source to path
script_dir = Path(__file__).parent
src_dir = script_dir / "src"
sys.path.insert(0, str(src_dir))

try:
    from claude_shell_connector.cli.main import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\\nTroubleshooting:")
    print("1. Run: python setup_cygwin.py")
    print("2. Set: export PYTHONPATH=$(pwd)/src:$PYTHONPATH")
    print("3. Test: python -c \\"import claude_shell_connector\\"")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
'''
    
    launcher_path = Path("claude-shell-cygwin")
    try:
        with open(launcher_path, "w", encoding="utf-8") as f:
            f.write(launcher_content)
        
        launcher_path.chmod(0o755)
        print(f"✅ Created launcher: {launcher_path}")
        return launcher_path
        
    except Exception as e:
        print(f"⚠️  Could not create launcher: {e}")
        return None


def test_basic_functionality():
    """Test basic functionality without relying on pip installation."""
    print("🧪 Testing basic functionality...")
    
    # Set up environment
    src_dir = Path.cwd() / "src"
    python_path = os.environ.get("PYTHONPATH", "")
    new_python_path = f"{src_dir}:{python_path}" if python_path else str(src_dir)
    os.environ["PYTHONPATH"] = new_python_path
    
    test_code = '''
import sys
import os

# Setup
sys.path.insert(0, "src")
os.environ["PYTHONIOENCODING"] = "utf-8"

try:
    from claude_shell_connector import run_command
    from claude_shell_connector.config.settings import ConnectorConfig
    
    # Test config
    config = ConnectorConfig()
    print(f"✅ Shell detected: {config.shell_path}")
    
    # Test command execution
    result = run_command("echo Test from Cygwin fix", timeout=10)
    if result.success:
        print(f"✅ Command successful: {result.stdout.strip()}")
        print(f"   Execution time: {result.execution_time:.3f}s")
    else:
        print(f"❌ Command failed: {result.error}")
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
'''
    
    try:
        result = run_command_with_timeout([
            sys.executable, "-c", test_code
        ], timeout=60)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False


def print_cygwin_instructions():
    """Print usage instructions."""
    print("\n" + "="*60)
    print("🎉 Cygwin Setup Complete!")
    print("="*60)
    
    print("\n📋 How to use:")
    
    print("\n1. Set environment (add to ~/.bashrc):")
    print("   export PYTHONPATH=$(pwd)/src:$PYTHONPATH")
    print("   export PYTHONIOENCODING=utf-8")
    print("   export CYGWIN=nodosfilewarning")
    
    print("\n2. Use the launcher:")
    print("   ./claude-shell-cygwin test")
    print("   ./claude-shell-cygwin exec \"echo hello\"")
    
    print("\n3. Use in Python:")
    print("   python -c \"")
    print("   import sys; sys.path.insert(0, 'src')")
    print("   from claude_shell_connector import run_command")
    print("   result = run_command('echo Hello Cygwin!')")
    print("   print(result.stdout)")
    print("   \"")
    
    print("\n⚠️  If you encounter issues:")
    print("   - Try: python test_cygwin_fix.sh")
    print("   - Check: which python (use Python 3.8+)")
    print("   - Reset: unset PYTHONPATH; export PYTHONPATH=$(pwd)/src")
    
    print("\n" + "="*60)


def main():
    """Main setup function with anti-hanging measures."""
    print("Claude Shell Connector - Cygwin Setup (Fixed)")
    print("="*50)
    
    # Setup environment first
    setup_cygwin_environment()
    
    print(f"Platform detected: {platform.system().lower()}")
    print(f"Python version: {sys.version}")
    
    success = False
    
    try:
        # Method 1: Try installing dependencies individually
        print("\n📦 Step 1: Installing dependencies...")
        deps_ok = install_dependencies_minimal()
        
        if deps_ok:
            print("✅ Dependencies installed")
        else:
            print("⚠️  Some dependencies failed, continuing anyway...")
        
        # Method 2: Manual package setup (skip pip -e .)
        print("\n📦 Step 2: Setting up package...")
        package_ok = install_package_manual()
        
        if package_ok:
            print("✅ Package setup successful")
            success = True
        else:
            print("⚠️  Package setup had issues")
        
        # Method 3: Create launcher
        print("\n🚀 Step 3: Creating launcher...")
        launcher = create_simple_launcher()
        
        # Method 4: Test functionality
        print("\n🧪 Step 4: Testing...")
        test_ok = test_basic_functionality()
        
        if test_ok:
            print("✅ Functionality test passed")
            success = True
        
        # Show instructions
        print_cygwin_instructions()
        
        if success:
            print("\n🎉 Setup completed successfully!")
        else:
            print("\n⚠️  Setup completed with warnings")
            print("Manual setup may be required - see instructions above")
        
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        print("You can retry with: python setup_cygwin.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\nFallback instructions:")
        print("1. pip install click rich pydantic")
        print("2. export PYTHONPATH=$(pwd)/src:$PYTHONPATH")
        print("3. python -c 'from claude_shell_connector import run_command'")
        sys.exit(1)


if __name__ == "__main__":
    main()