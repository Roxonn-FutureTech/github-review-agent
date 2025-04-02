# Contributing to GitHub Review Agent

First off, thank you for considering contributing to GitHub Review Agent! It's people like you that make GitHub Review Agent such a great tool.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include screenshots if possible

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

## Development Process

1. Clone the repository

    ```bash
    git clone https://github.com/Roxonn-FutureTech/github-review-agent.git
    cd github-review-agent
    ```

2. Create a branch

    ```bash
    git checkout -b feature/your-feature-name
    ```

3. Set up development environment

    ```bash
    pip install -r src/backend/requirements.txt
    cp config/.env.example config/.env
    ```

4. Make your changes and test them

5. Commit your changes

    ```bash
    git add .
    git commit -m "feat: Add your feature description"
    ```

6. Push to your fork

    ```bash
    git push origin feature/your-feature-name
    ```

## Coding Guidelines

### Python Style Guide

* Follow PEP 8 style guide
* Use meaningful variable and function names
* Add docstrings to all functions and classes
* Keep functions focused and single-purpose
* Maximum line length of 100 characters

### Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Documentation

* Update the README.md if needed
* Add docstrings to Python functions and classes
* Comment complex algorithms or business logic
* Update API documentation for any endpoint changes

<<<<<<< HEAD
=======
## Logging Guidelines

When adding new code, follow these logging practices:

1. Always use the project's logging system:
   ```python
   from ai_engine.logging_config import get_logger
   
   logger = get_logger(__name__)
   ```

2. Use appropriate log levels:
   - ERROR: For errors that prevent normal operation
   - WARNING: For unexpected but handled situations
   - INFO: For significant events in normal operation
   - DEBUG: For detailed debugging information

3. Include relevant context in log messages:
   ```python
   logger.info(f"Processing file: {filename}")
   logger.error(f"Failed to parse {filename}", extra={'error': str(e)})
   ```

4. Log files are stored in the `logs` directory with automatic rotation

>>>>>>> feature/ai-engine-core
## Testing

* Write unit tests for new features
* Ensure all tests pass before submitting PR
* Include integration tests where necessary
* Test edge cases and error conditions

### Running Tests

```bash
python -m pytest tests/
```

## Project Structure

```text
github-review-agent/
├── README.md
├── LICENSE
├── src/
│   ├── backend/
│   │   ├── main.py
│   │   └── requirements.txt
│   └── ai_engine/
│       └── code_analyzer.py
├── config/
│   └── .env.example
└── docs/
    ├── CONTRIBUTING.md
    ├── API.md
    ├── TROUBLESHOOTING.md
    └── ISSUES.md
```

## Review Process

1. All PRs must be reviewed by at least one maintainer
2. Address all comments and requested changes
3. Ensure CI/CD pipeline passes
4. Keep PRs focused and single-purpose
5. Large changes should be discussed in issues first

## Additional Notes

### Issue Labels

* `bug`: Something isn't working
* `enhancement`: New feature or request
* `documentation`: Improvements or additions to documentation
* `good first issue`: Good for newcomers
* `help wanted`: Extra attention is needed

## Recognition

Contributors will be recognized in:

* The project's README
* Our official documentation
* Release notes

Thank you for contributing to GitHub Review Agent! 🎉
<<<<<<< HEAD
=======

>>>>>>> feature/ai-engine-core
