# Contributing to Hands Trapezium

Thank you for your interest in contributing to Hands Scaphoid! This document provides guidelines and information for contributors.

## Ways to contribute

- **Bug reports**: Report bugs through GitHub issues
- **Feature requests**: Suggest new features or improvements
- **Code contributions**: Submit pull requests with bug fixes or new features
- **Documentation**: Improve documentation, examples, or tutorials
- **Testing**: Help improve test coverage or add integration tests

## Getting Started

### Development environment setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/{github-user-name}/hands_scaphoid.git
   cd hands_scaphoid
   ```

2. **Install development dependencies**
   ```bash
   # Using UV (recommended)
   uv sync --extra dev
   
   # Or using pip
   pip install -e ".[dev]"
   ```

3. **Verify installation**
   ```bash
   # Run tests
   pytest
   
   # Check linting
   flake8 src tests 
   
   # Check type hints
   mypy src
   ```

### Development tools

We use several tools to maintain code quality:

- **Ruff**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **pytest**: Testing
- **pre-commit**: Git hooks

## Testing

### Running tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_shell.py

# Run specific test
pytest tests/test_shell.py::TestShellRunMethod::test_run_allowed_command
```

### Writing tests

- Place tests in the `tests/` directory
- Use descriptive test names that explain what is being tested
- Follow the existing test structure and naming conventions
- Include both positive and negative test cases
- Mock external dependencies where appropriate

Example test structure:
```python
class TestFeatureName:
    """Test suite for FeatureName."""
    
    def test_feature_with_valid_input(self):
        """Test that feature works with valid input."""
        # Arrange
        # Act
        # Assert
        
    def test_feature_with_invalid_input(self):
        """Test that feature handles invalid input correctly."""
        # Test error handling
```

### Test categories

- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test component interactions
- **Security tests**: Test security features and edge cases

## Code style

### Code formatting

We use Ruff for code formatting with these settings:
- Line length: 88 characters
- Target Python version: 3.11+

Format your code before submitting:
```bash
ruff format src tests
isort src tests
```

### Docstring style

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of the function.
    
    Longer description if needed. Explain the purpose, behavior,
    and any important details.
    
    Args:
        param1: Description of param1.
        param2: Description of param2.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: When param1 is empty.
        TypeError: When param2 is not an integer.
        
    Example:
        >>> result = example_function("hello", 42)
        >>> print(result)
        True
    """
```

### Type Hints

- Use type hints for all function parameters and return values
- Import types from `typing` module when needed
- Use `Optional[T]` for nullable values
- Use `Union[T, U]` for multiple possible types

## 🔐 Security Guidelines

When contributing to Hands Trapezium's security features:

1. **Never disable security checks** without proper justification
2. **Test security edge cases** thoroughly
3. **Document security implications** of changes
4. **Follow the principle of least privilege**
5. **Validate all user inputs**

## 📋 Pull Request Process

### Before Submitting

1. **Create an Issue**: For new features or major changes, create an issue first to discuss the approach
2. **Branch Naming**: Use descriptive branch names:
   - `feature/add-new-command-type`
   - `bugfix/fix-environment-loading`
   - `docs/improve-api-reference`
3. **Code Quality**: Ensure your code passes all checks:
   ```bash
   # Format code
   black src tests
   isort src tests
   
   # Check linting
   flake8 src tests
   
   # Type checking
   mypy src
   
   # Run tests
   pytest
   ```

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New code is covered by tests
- [ ] Documentation is updated if needed
- [ ] CHANGELOG.md is updated for user-facing changes
- [ ] Commit messages are clear and descriptive
- [ ] No unnecessary changes or files are included

### Pull Request Template

```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests added for new functionality
- [ ] All tests pass
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**:
   - Python version
   - Operating system
   - hands-trapezium version
   
2. **Steps to Reproduce**:
   - Minimal code example
   - Expected behavior
   - Actual behavior
   
3. **Additional Context**:
   - Error messages or logs
   - Screenshots if applicable
   - Any relevant configuration

## 💡 Feature Requests

When requesting features:

1. **Use Case**: Describe the problem you're trying to solve
2. **Proposed Solution**: Suggest how it might work
3. **Alternatives**: Consider alternative approaches
4. **Impact**: Estimate how many users would benefit

## 📚 Documentation

### Building Documentation

```bash
# Install documentation dependencies
uv sync --extra docs

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

### Documentation Guidelines

- Use clear, concise language
- Include code examples
- Test code examples to ensure they work
- Update API documentation when changing code
- Follow existing documentation structure

## 🏷️ Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## ❓ Questions

If you have questions about contributing:

1. Check existing issues and discussions
2. Create a new issue with the "question" label
3. Reach out to maintainers

## 🙏 Recognition

Contributors are recognized in:
- README.md
- Release notes
- Documentation credits

Thank you for contributing to Hands Trapezium! 🎉
