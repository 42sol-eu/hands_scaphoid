# DNA.py Wheel Installation Guide

Your `dna.py` script now has built-in wheel file installation support! Here's how to use it:

## 🎯 Quick Start

### Method 1: Automatic Installation (Recommended)
```bash
# Your script will automatically check and install missing dependencies
python dna.py find-classes --auto-install

# Or set auto-install as default behavior
python dna.py --auto-install find-classes
```

### Method 2: Manual Wheel Installation
```bash
# Install from existing wheel files in dist/
python dna.py install-wheels

# Create dist folder, download wheels, then install
python dna.py install-wheels --create-dist
```

### Method 3: Direct Wheel Installation
```bash
# Install specific packages from wheel files
python -m pip install dist/copier-9.10.2-py3-none-any.whl
python -m pip install dist/rich_cli-1.8.1-py3-none-any.whl
python -m pip install dist/rich_click-1.9.1-py3-none-any.whl

# Or install all at once
python -m pip install dist/*.whl
```

## 📁 Directory Structure

Your dna folder now has this structure:
```
dna/
├── dna.py                      # Main script with wheel support
├── dist/                       # Local wheel files
│   ├── copier-9.10.2-py3-none-any.whl
│   ├── rich_cli-1.8.1-py3-none-any.whl
│   ├── rich_click-1.9.1-py3-none-any.whl
│   └── ... (35+ dependency wheels)
├── commands/                   # Your command modules
└── requirements-local.txt      # Requirements file for wheels
```

## 🔧 How It Works

Your modified `dna.py` includes several key functions:

### 1. `ensure_dependencies_installed()`
- Checks if required packages are available
- Attempts installation from local wheels first
- Falls back to PyPI if wheels aren't available
- Called automatically when script starts

### 2. `install_wheels_command()`
- Manually installs packages from dist/ folder
- Handles missing dist folder gracefully
- Provides detailed feedback during installation

### 3. CLI Integration
- New `install-wheels` command for manual control
- `--auto-install` flag for automatic dependency handling
- Graceful fallbacks when command modules aren't available

## 📦 Wheel File Management

### Download Wheels
```bash
# Download wheels for your dependencies
pip download copier rich-cli rich-click --dest dna/dist --only-binary=:all:

# Download with specific versions
pip download "copier>=9.10.2" "rich-cli>=1.8.0" --dest dna/dist --only-binary=:all:
```

### Using UV (Alternative)
```bash
# Install using UV with local wheels
cd dna
uv pip install --find-links dist copier rich-cli rich-click

# Or install specific wheel files
uv pip install dist/copier-9.10.2-py3-none-any.whl
```

## 🚀 Usage Examples

### Example 1: First Time Setup
```bash
# 1. Create your dist folder and download wheels
python dna.py install-wheels --create-dist

# 2. Now use your script normally
python dna.py find-classes src/
```

### Example 2: Offline Environment  
```bash
# Pre-download wheels on a connected machine
pip download copier rich-cli rich-click --dest dna/dist --only-binary=:all:

# Transfer dist/ folder to offline machine
# Script will work without internet connection
python dna.py --auto-install find-classes
```

### Example 3: Development Workflow
```bash
# Install development dependencies
python dna.py install-wheels

# Use your script with all features
python dna.py find-classes --recursive src/
python dna.py check-init src/package/__init__.py
python dna.py create-file newmodule.py --template class
```

## 🔍 Troubleshooting

### Missing Dependencies
If you see: `ModuleNotFoundError: No module named 'rich_click'`

**Solutions:**
1. `python dna.py install-wheels --create-dist`
2. `python -m pip install dist/rich_click-*.whl`  
3. `python dna.py --auto-install <command>`

### Missing Commands
If you see: `⚠️ class_finder not available - install commands module`

**Solutions:**
1. Create the missing command modules in `commands/` folder
2. Use the basic functionality until commands are implemented
3. Install from wheel that includes command modules

### Permission Issues
If you see permission errors during installation:

**Solutions:**
1. Use `--user` flag: `python -m pip install --user dist/*.whl`
2. Use virtual environment: `python -m venv .venv && .venv\Scripts\activate`
3. Run as administrator (Windows) or use `sudo` (Linux/Mac)

## 💡 Best Practices

### 1. Version Pinning
```bash
# Pin exact versions in your PEP 723 header
# /// script
# dependencies = [
#     "rich-click==1.9.1",
#     "copier==9.10.2", 
# ]
# ///
```

### 2. Offline-First Development
```bash
# Always create local wheels for dependencies
pip download -r requirements.txt --dest dist --only-binary=:all:

# Test offline capability
python dna.py --auto-install <command>
```

### 3. Distribution
```bash
# Include dist/ folder when sharing your script
tar -czf dna-toolkit.tar.gz dna/

# Recipients can use immediately without internet
tar -xzf dna-toolkit.tar.gz
cd dna
python dna.py --auto-install find-classes
```

## 🎉 Benefits

✅ **Offline Capability** - Works without internet after initial setup  
✅ **Version Control** - Exact dependency versions guaranteed  
✅ **Fast Installation** - No compilation or download time  
✅ **Security** - No dependency confusion attacks  
✅ **Portability** - Share complete toolkit with dependencies  
✅ **Reliability** - Dependencies can't disappear from PyPI  

Your `dna.py` script is now a self-contained toolkit that can manage its own dependencies from wheel files! 🧬