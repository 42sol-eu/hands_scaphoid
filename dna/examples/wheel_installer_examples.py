#!/usr/bin/env python3
"""
Example script showing how to handle wheel file installation in dna.py

This script demonstrates different approaches to automatically install
wheel files when dependencies are not available.
"""

import sys
import subprocess
from pathlib import Path
import importlib.util


def method_1_simple_check_and_install():
    """Simple approach: Check if package exists, install from wheel if not."""
    
    def is_package_installed(package_name):
        """Check if a package is installed."""
        return importlib.util.find_spec(package_name) is not None
    
    def install_from_wheel(wheel_path):
        """Install package from wheel file."""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', str(wheel_path)
            ], capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    # Check for copier
    if not is_package_installed('copier'):
        print("📦 Copier not found, looking for wheel file...")
        
        # Look for copier wheel in dist/
        dist_path = Path('../dist')
        copier_wheels = list(dist_path.glob('copier-*.whl'))
        
        if copier_wheels:
            print(f"📥 Installing copier from {copier_wheels[0].name}")
            if install_from_wheel(copier_wheels[0]):
                print("✅ Copier installed successfully!")
            else:
                print("❌ Failed to install copier")
        else:
            print("⚠️ No copier wheel found in dist/")


def method_2_uv_installation():
    """Use UV to install from local wheels."""
    
    def install_with_uv(package_name, dist_path):
        """Install package using UV with find-links."""
        try:
            result = subprocess.run([
                'uv', 'pip', 'install', 
                '--find-links', str(dist_path),
                package_name
            ], capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    dist_path = Path('../dist')
    if dist_path.exists():
        packages = ['copier', 'rich-cli']
        
        for package in packages:
            print(f"📦 Installing {package} with UV...")
            if install_with_uv(package, dist_path):
                print(f"✅ {package} installed successfully!")
            else:
                print(f"❌ Failed to install {package}")


def method_3_requirements_file():
    """Create and use requirements file with local wheels."""
    
    def create_local_requirements():
        """Create requirements file with local wheel paths."""
        dist_path = Path('../dist')
        requirements = []
        
        if dist_path.exists():
            # Find main packages
            for pattern in ['copier-*.whl', 'rich_cli-*.whl']:
                wheels = list(dist_path.glob(pattern))
                if wheels:
                    requirements.append(f"./dist/{wheels[0].name}")
        
        # Write requirements file
        req_file = Path('requirements-local.txt')
        with open(req_file, 'w') as f:
            f.write('\n'.join(requirements))
        
        return req_file
    
    def install_from_requirements(req_file):
        """Install from requirements file."""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                '-r', str(req_file)
            ], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    print("📋 Creating local requirements file...")
    req_file = create_local_requirements()
    
    if req_file.exists():
        print(f"📥 Installing from {req_file}")
        if install_from_requirements(req_file):
            print("✅ Packages installed from requirements file!")
        else:
            print("❌ Failed to install from requirements file")


def method_4_fallback_strategy():
    """Comprehensive fallback strategy: wheels -> PyPI -> error."""
    
    def try_install_package(package_name, package_module=None):
        """Try installing package with multiple fallback methods."""
        module_name = package_module or package_name.replace('-', '_')
        
        # Check if already installed
        if importlib.util.find_spec(module_name):
            print(f"✅ {package_name} already installed")
            return True
        
        print(f"📦 {package_name} not found, attempting installation...")
        
        # Method 1: Try local wheel
        dist_path = Path('../dist')
        if dist_path.exists():
            wheels = list(dist_path.glob(f'{package_name.replace("-", "_")}-*.whl'))
            if wheels:
                print(f"📥 Installing {package_name} from {wheels[0].name}")
                try:
                    subprocess.run([
                        sys.executable, '-m', 'pip', 'install', str(wheels[0])
                    ], check=True)
                    print(f"✅ {package_name} installed from wheel!")
                    return True
                except subprocess.CalledProcessError:
                    print(f"❌ Failed to install {package_name} from wheel")
        
        # Method 2: Try UV with find-links
        try:
            subprocess.run([
                'uv', 'pip', 'install', 
                '--find-links', str(dist_path), 
                package_name
            ], check=True)
            print(f"✅ {package_name} installed with UV!")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Method 3: Fallback to PyPI
        print(f"📡 Installing {package_name} from PyPI...")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', package_name
            ], check=True)
            print(f"✅ {package_name} installed from PyPI!")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package_name} from PyPI")
            return False
    
    # Install required packages
    packages = [
        ('copier', 'copier'),
        ('rich-cli', 'rich_cli'),
        ('rich-click', 'rich_click')
    ]
    
    all_success = True
    for package_name, module_name in packages:
        if not try_install_package(package_name, module_name):
            all_success = False
    
    return all_success


if __name__ == '__main__':
    print("🧬 DNA Wheel Installation Examples\n")
    
    print("=" * 50)
    print("Method 1: Simple Check and Install")
    print("=" * 50)
    method_1_simple_check_and_install()
    
    print("\n" + "=" * 50)
    print("Method 2: UV Installation") 
    print("=" * 50)
    method_2_uv_installation()
    
    print("\n" + "=" * 50)
    print("Method 3: Requirements File")
    print("=" * 50)
    method_3_requirements_file()
    
    print("\n" + "=" * 50)
    print("Method 4: Comprehensive Fallback")
    print("=" * 50)
    success = method_4_fallback_strategy()
    
    if success:
        print("\n🎉 All packages installed successfully!")
    else:
        print("\n❌ Some packages failed to install")