"""
Simple wheel installation integration for dna.py

Add this code to your dna.py to automatically handle wheel installations.
"""

# Add this function after your imports in dna.py:

def ensure_wheel_dependencies():
    """
    Ensure wheel dependencies are installed, create dist if needed.
    
    Returns True if all dependencies are available, False otherwise.
    """
    import importlib.util
    import subprocess
    from pathlib import Path
    
    # Check required packages
    required = {
        'copier': 'copier',
        'rich_click': 'rich-click', 
        # Add more as needed
    }
    
    missing = []
    for module, package in required.items():
        if not importlib.util.find_spec(module):
            missing.append(package)
    
    if not missing:
        return True
    
    print(f"📦 Missing packages: {', '.join(missing)}")
    
    # Check for dist folder and wheels
    dist_path = Path(__file__).parent.parent / 'dist'
    
    if not dist_path.exists():
        print("📁 Creating dist folder and downloading wheels...")
        dist_path.mkdir(exist_ok=True)
        
        # Download wheels
        try:
            subprocess.run([
                'pip', 'download', 'copier', 'rich-cli', 'rich-click',
                '--dest', str(dist_path),
                '--only-binary=:all:'
            ], check=True)
            print("✅ Wheels downloaded successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to download wheels")
            return False
    
    # Install missing packages from wheels
    for package in missing:
        wheels = list(dist_path.glob(f'{package.replace("-", "_")}-*.whl'))
        if wheels:
            print(f"📥 Installing {package} from wheel...")
            try:
                subprocess.run([
                    'pip', 'install', str(wheels[0])
                ], check=True)
                print(f"✅ {package} installed!")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    return True


# Add this to the beginning of your main() or cli() function:

def main():
    """Modified main function with wheel dependency checking."""
    
    # Ensure dependencies are available
    if not ensure_wheel_dependencies():
        print("❌ Could not install required dependencies")
        sys.exit(1)
    
    # Now proceed with your normal CLI logic
    cli()


# Usage examples for command line:

# 1. Simple usage - automatically handles missing deps:
# python dna.py find-classes

# 2. Force reinstall dependencies:
# python dna.py install-wheels --create-dist

# 3. Manual wheel management:
# python -c "from dna import ensure_wheel_dependencies; ensure_wheel_dependencies()"