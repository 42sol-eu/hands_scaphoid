# [Local imports]
from .check_init import console

def install_wheels_command():
    """Command to manually install wheel dependencies."""
    dist_path = Path(__file__).parent.parent / 'dist'
    
    if not dist_path.exists():
        console.print(f"❌ [red]No dist directory found at: {dist_path}[/red]")
        console.print("💡 Create wheel files first with:")
        console.print("   pip download copier rich-cli rich-click --dest dist --only-binary=:all:")
        return False
    
    wheel_files = list(dist_path.glob('*.whl'))
    if not wheel_files:
        console.print(f"❌ [red]No wheel files found in: {dist_path}[/red]")
        return False
    
    console.print(f"📦 Found {len(wheel_files)} wheel files in dist/")
    
    # Install main packages
    main_packages = ['copier', 'rich_cli', 'rich_click']
    
    for package in main_packages:
        matching_wheels = [w for w in wheel_files if package.replace('-', '_') in w.name.lower()]
        if matching_wheels:
            wheel_file = matching_wheels[0]
            console.print(f"📥 Installing {wheel_file.name}")
            
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', str(wheel_file)
                ], check=True)
                console.print(f"✅ Successfully installed {package}")
            except subprocess.CalledProcessError as e:
                console.print(f"❌ Failed to install {package}: {e}")
    
    return True
