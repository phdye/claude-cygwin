# Contributing to Claude Shell Connector

We welcome contributions! This document provides guidelines for contributing to the project.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/claude-shell-connector.git
   cd claude-shell-connector
   ```
3. **Set up development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   make install-dev
   ```

## 🛠️ Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- A shell environment (Cygwin, WSL, or Unix)

### Installation
```bash
# Install in development mode with all dependencies
make install-dev

# Or manually:
pip install -e .[dev]
pre-commit install
```

### Development Commands
```bash
# Run tests
make test

# Run linting
make lint

# Format code
make format

# Build package
make build

# Clean build artifacts
make clean
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=claude_shell_connector

# Run only unit tests
pytest -m "not integration"

# Run only integration tests
pytest -m integration

# Run tests for specific shell
SHELL_TYPE=bash pytest tests/test_integration.py
```

### Writing Tests
- Place tests in the `tests/` directory
- Use descriptive test names: `test_should_execute_command_successfully`
- Mark integration tests: `@pytest.mark.integration`
- Mock external dependencies when possible
- Test both success and failure cases

### Test Categories
- **Unit tests**: Test individual functions/classes in isolation
- **Integration tests**: Test shell execution with real environments
- **CLI tests**: Test command-line interface functionality

## 📝 Code Style

We use several tools to maintain code quality:

### Formatting
- **Black**: Code formatting (`black src tests`)
- **isort**: Import sorting (`isort src tests`)

### Linting
- **Flake8**: Style and error checking (`flake8 src tests`)
- **MyPy**: Type checking (`mypy src`)

### Pre-commit Hooks
Pre-commit hooks run automatically on `git commit`:
```bash
pre-commit install  # Set up hooks
pre-commit run --all-files  # Run manually
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Python version** (`python --version`)
2. **Operating system** and version
3. **Shell environment** (Cygwin, WSL, etc.)
4. **Steps to reproduce** the issue
5. **Expected behavior** vs **actual behavior**
6. **Error messages** and stack traces
7. **Configuration** used (sanitized)

### Bug Report Template
```
**Environment:**
- OS: Windows 11 / Ubuntu 22.04 / macOS 13
- Python: 3.11.0
- Shell: Cygwin 3.4.0
- Package version: 1.0.0

**Steps to Reproduce:**
1. Run `claude-shell start`
2. Execute command: `echo 'test'`
3. Observe error

**Expected:** Command should execute successfully
**Actual:** TimeoutError after 30 seconds

**Error Message:**
```
TimeoutError: Command timed out after 30 seconds
```

**Configuration:**
- work_dir: ./claude_connector
- shell_path: C:\cygwin64\bin\bash.exe
- timeout: 30
```

## 💡 Feature Requests

For new features:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** clearly
3. **Provide examples** of how it would work
4. **Consider backwards compatibility**
5. **Discuss implementation approach** if possible

## 🔧 Development Guidelines

### Code Organization
```
src/claude_shell_connector/
├── core/          # Core functionality
├── config/        # Configuration management
├── helpers/       # Utility functions
├── cli/           # Command-line interface
└── plugins/       # Shell-specific plugins (future)
```

### Coding Standards
- **Type hints**: Use type hints for all functions
- **Docstrings**: Document all public functions and classes
- **Error handling**: Use specific exception types
- **Logging**: Use structured logging with appropriate levels
- **Configuration**: Make everything configurable
- **Security**: Validate inputs and sanitize outputs

### Git Workflow
1. **Create feature branch**: `git checkout -b feature/new-feature`
2. **Make changes** with clear, focused commits
3. **Test thoroughly** (`make test`)
4. **Update documentation** as needed
5. **Submit pull request** with description

### Commit Messages
Use conventional commit format:
```
type(scope): description

feat(cli): add new status command
fix(core): handle timeout errors gracefully
docs(readme): update installation instructions
test(integration): add cygwin-specific tests
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `style`, `chore`

## 📚 Documentation

### Updating Documentation
- **README.md**: Overview and quick start
- **API docs**: Docstrings in code
- **Examples**: Add to `examples/` directory
- **Changelog**: Update `CHANGELOG.md`

### Documentation Guidelines
- Use clear, concise language
- Provide working examples
- Include common use cases
- Link to related sections
- Keep up-to-date with code changes

## 🔒 Security

### Security Guidelines
- **Input validation**: Sanitize all command inputs
- **Path traversal**: Prevent directory traversal attacks
- **Command injection**: Use parameterized commands
- **Resource limits**: Implement timeouts and size limits
- **Permissions**: Run with minimal required permissions

### Reporting Security Issues
For security vulnerabilities:
1. **DO NOT** open a public issue
2. **Email** security@yourproject.com (if available)
3. **Provide details** about the vulnerability
4. **Allow time** for responsible disclosure

## 🎯 Pull Request Process

1. **Fork and branch** from `main`
2. **Follow coding standards** and run tests
3. **Update documentation** if needed
4. **Add changelog entry** for user-facing changes
5. **Create pull request** with:
   - Clear title and description
   - Link to related issues
   - Screenshots for UI changes
   - Test results

### PR Checklist
- [ ] Tests pass (`make test`)
- [ ] Code is formatted (`make format`)
- [ ] Linting passes (`make lint`)
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] No breaking changes (or clearly documented)

## 🏆 Recognition

Contributors will be recognized in:
- **README.md** contributors section
- **CHANGELOG.md** for significant contributions
- **GitHub releases** for major features

## 📞 Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community support
- **Documentation**: Check docs first
- **Examples**: See `examples/` directory

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Claude Shell Connector! 🎉