---
applyTo: "**/pyproject.toml"
---
# Project configuration standards

## Project Metadata
- Maintain consistent version format: `YYYY.MAJOR.MINOR`
- Use semantic authors format with email
- Include comprehensive dependency specifications

## Tool Configuration
```toml 
# ---yaml
# File:
#    name: pyproject.toml
#    uuid: {{generated-uuid}}
#    date: {{modification date, YYYY-MM-DD}}
#
# Description:
#    Python library configuration
#
# Project:
#    name: hands_scaphoid
#    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
#    url: https://github.com/42sol-eu/hands_scaphoid
#
# Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
#
# Abbreviations:
# - {{abbreviation}}[{{context}}]:: {{description}}
# - TOML[file]: Tom's Obvious, Minimal Language (file format)
#

[tool.pytest.ini_options]
testpaths = ["tests"]
# Coverage reporting disabled by default for performance

[tool.ruff]
# Ignore logging format rules (G201-G204) - f-strings allowed in logging
ignore = ["G201", "G202", "G203", "G204"]

[tool.pylint]
# W1203 disabled - f-string logging is allowed in this project
disable = "W1203"
```

## Dependency Groups
- Separate dev, test, and docs dependencies
- Use version constraints for stability
- Include Rich ecosystem packages:
  - `rich>=13.0.0` for console output
  - `rich-click>=1.9.1` for CLI interfaces

## Build System
- Use modern setuptools with `build-backend = "setuptools.build_meta"`
- Require Python 3.13+ for latest features
- Include development tools in optional dependencies