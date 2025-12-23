# Contributing to aidocs-cli

Thank you for your interest in contributing to aidocs-cli!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/binarcode/aidocs-cli.git
   cd aidocs-cli
   ```

2. Install dependencies with uv:
   ```bash
   uv sync
   ```

3. Run locally:
   ```bash
   uv run aidocs --help
   ```

## Making Changes

### Version Bump Required

**Important:** When creating a PR, you must update the version number in two files:

1. `pyproject.toml` - Update the `version` field
2. `src/aidocs_cli/__init__.py` - Update the `__version__` variable

Both files must have the same version number.

### Version Format

We use [Semantic Versioning](https://semver.org/):

- **Patch** (0.15.x → 0.15.y): Bug fixes, minor changes
- **Minor** (0.x.0 → 0.y.0): New features, non-breaking changes
- **Major** (x.0.0 → y.0.0): Breaking changes

### Why?

Our release workflow reads the version from `pyproject.toml` and automatically:
- Creates a GitHub release with that version
- Publishes to PyPI
- Updates the Homebrew formula

If you don't bump the version, no release will be created when your PR is merged.

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. **Bump the version** in both files
5. Commit your changes
6. Push to your fork
7. Open a Pull Request

## Code Style

- Follow PEP 8 for Python code
- Use type hints where possible
- Keep functions focused and well-documented

## Questions?

Open an issue if you have questions or need help.
