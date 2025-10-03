# [Standard library imports]
import os
import sys
import subprocess
import importlib.util
from pathlib import Path

# [Local imports]
from .check_init import console

# [Third party imports - with fallback for when not available]

# [Code]
def ensure_dependencies_installed():
    """
    Ensure required dependencies are installed from wheel files if available.
    
    This function checks if required packages are available and attempts to
    install them from local wheel files in the dist/ directory if not found.
    """
    required_packages = {
        'rich_click': 'rich-click',
        'copier': 'copier', 
        'rich': 'rich'
    }
    
    missing_packages = []
    
    # Check which packages are missing
    for module_name, package_name in required_packages.items():
        if importlib.util.find_spec(module_name) is None:
            missing_packages.append(package_name)
    
    if not missing_packages:
        return True
    
    # Try to install from local wheels first
    dist_path = Path(__file__).parent.parent / 'dist'
    if dist_path.exists():
        print(f"📦 Found dist directory at: {dist_path}")
        
        # Look for wheel files
        wheel_files = list(dist_path.glob('*.whl'))
        if wheel_files:
            print(f"🔍 Found {len(wheel_files)} wheel files")
            
            # Try installing missing packages from wheels
            for package in missing_packages:
                matching_wheels = [w for w in wheel_files if package.replace('-', '_') in w.name.lower()]
                if matching_wheels:
                    wheel_file = matching_wheels[0]  # Use first match
                    console.print(f"📥 Installing {package} from {wheel_file.name}")
                    
                    try:
                        result = subprocess.run([
                            sys.executable, '-m', 'pip', 'install', str(wheel_file)
                        ], capture_output=True, text=True, check=True)
                        console.print(f"✅ Successfully installed {package}")
                    except subprocess.CalledProcessError as e:
                        console.print(f"❌ Failed to install {package}: {e}")
                        return False
                else:
                    console.print(f"⚠️ No wheel file found for {package}")
    
    # If wheels didn't work, try installing from PyPI
    if missing_packages:
        console.print("📡 Attempting to install missing packages from PyPI...")
        for package in missing_packages:
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], capture_output=True, text=True, check=True)
                console.print(f"✅ Successfully installed {package} from PyPI")
            except subprocess.CalledProcessError as e:
                console.print(f"❌ Failed to install {package} from PyPI: {e}")
                return False
    
    return True

