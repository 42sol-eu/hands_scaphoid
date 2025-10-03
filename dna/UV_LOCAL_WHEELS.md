# Using UV with Local Wheel Files

This document shows different ways to use `uv` with local wheel files for `copier` and `rich-cli`.

## 📁 Directory Structure

```
dna/
├── dist/                          # Local wheel files directory
│   ├── copier-9.10.2-py3-none-any.whl
│   ├── rich_cli-1.8.1-py3-none-any.whl
│   └── ... (all dependencies)
├── requirements-local.txt         # Requirements file with local wheels
└── example-pyproject.toml        # Example project configuration
```

## 🎯 Method 1: Direct Installation

Install directly from local wheel files:

```bash
# Install copier from local wheel
uv pip install dist/copier-9.10.2-py3-none-any.whl

# Install rich-cli from local wheel  
uv pip install dist/rich_cli-1.8.1-py3-none-any.whl

# Install multiple wheels at once
uv pip install dist/copier-9.10.2-py3-none-any.whl dist/rich_cli-1.8.1-py3-none-any.whl
```

## 📋 Method 2: Requirements File

Use `requirements-local.txt`:

```txt
# Local wheel installations
./dist/copier-9.10.2-py3-none-any.whl
./dist/rich_cli-1.8.1-py3-none-any.whl
```

Install with:
```bash
uv pip install -r requirements-local.txt
```

## 🏗️ Method 3: pyproject.toml

Specify local wheels in your project configuration:

```toml
[project]
name = "my-project"
dependencies = [
    # Absolute file URLs
    "copier @ file:///C:/_projects/42sol.eu/hands_scaphoid/dist/copier-9.10.2-py3-none-any.whl",
    "rich-cli @ file:///C:/_projects/42sol.eu/hands_scaphoid/dist/rich_cli-1.8.1-py3-none-any.whl",
]

[project.optional-dependencies]
dev = [
    # Relative file URLs (from project root)
    "copier @ file://./dist/copier-9.10.2-py3-none-any.whl",
    "rich-cli @ file://./dist/rich_cli-1.8.1-py3-none-any.whl",
]
```

## 🔍 Method 4: Find Links

Use `--find-links` to point to your local wheel directory:

```bash
# Install from local directory first, then PyPI if not found
uv pip install --find-links dist copier rich-cli

# Only use local directory (no PyPI)
uv pip install --find-links dist --no-index copier rich-cli
```

## 🔧 Method 5: UV Sync with Local Wheels

For projects using `uv.lock`:

```bash
# Add local wheels to your project
uv add ./dist/copier-9.10.2-py3-none-any.whl
uv add ./dist/rich_cli-1.8.1-py3-none-any.whl

# Sync environment
uv sync
```

## 📦 How the Wheels Were Downloaded

The wheel files were downloaded using pip:

```bash
pip download copier rich-cli --dest dist --only-binary=:all:
```

This downloads:
- ✅ `copier-9.10.2-py3-none-any.whl` - Main copier package
- ✅ `rich_cli-1.8.1-py3-none-any.whl` - Main rich-cli package  
- ✅ All 32 dependency wheels (click, requests, pydantic, etc.)

## 🧪 Testing the Installation

Test that the packages work:

```bash
# Test copier
copier --version
# Output: copier 9.4.1

# Test rich-cli (via python module)
python -m rich --version
# Shows rich feature overview with colorful output
```

## 💡 Benefits of Local Wheels

1. **Offline Installation** - No internet required after download
2. **Version Control** - Pin exact versions including dependencies
3. **Security** - No risk of dependency confusion attacks
4. **Speed** - Faster installs from local files
5. **Reproducibility** - Identical environments across systems

## 🚀 Best Practices

1. **Use `--only-binary=:all:`** when downloading to avoid compilation
2. **Store wheels in version control** for complete reproducibility
3. **Use relative paths** in pyproject.toml for portability
4. **Update wheels regularly** for security patches
5. **Document wheel sources** for maintainability

## 📚 UV Commands Summary

```bash
# Install from local wheel
uv pip install ./dist/package.whl

# Install from requirements file
uv pip install -r requirements-local.txt

# Install with find-links
uv pip install --find-links dist package-name

# Add to UV project
uv add ./dist/package.whl

# Sync UV project
uv sync
```

All methods work with `uv` and provide different levels of flexibility for your use case!