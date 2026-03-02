# Contributing to AIF

Thank you for your interest in contributing to the Adaptive Image Format project.

## Getting Started

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Run the test suite for the affected package(s)
5. Submit a pull request

## Development Setup

### Python (`packages/python`)

```bash
cd packages/python
pip install -e ".[dev]"
pytest
```

### JavaScript (`packages/js`)

```bash
cd packages/js
npm install
npm test
```

### Swift (`packages/swift`)

```bash
cd packages/swift
swift build
swift test
```

## Guidelines

### Code Style

- **Python**: Follow PEP 8. Use `ruff` for linting.
- **JavaScript/TypeScript**: Follow the existing style. TypeScript strict mode is enabled.
- **Swift**: Follow the Swift API Design Guidelines.

### AGPL Header

All new source files must include the AGPL-3.0 license header with `Copyright (C) 2026 Markus Köplin`. See any existing source file for the format.

### Tests

- All new features and bug fixes should include tests
- Run the relevant test suite before submitting a PR
- Aim for meaningful test coverage — don't just test trivial getters

### Commits

- Use clear, descriptive commit messages
- Reference issue numbers where applicable (`Fixes #123`)
- Keep commits focused — one logical change per commit

### Pull Requests

- Fill out the PR template
- Ensure CI passes
- Keep PRs focused and reasonably sized
- Describe what changed and why

## Reporting Issues

- Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.yml) for bugs
- Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.yml) for suggestions

## License

By contributing, you agree that your contributions will be licensed under the AGPL-3.0-or-later license. Copyright is assigned to Markus Köplin.
