# 🧰 RepoBuddy

**Your friendly GitHub repository assistant.** Check whether a local project is ready to share, and get concrete suggestions for improving it.

[![CI](https://github.com/lefebvreperrottearthur-stack/RepoBuddy/actions/workflows/ci.yml/badge.svg)](https://github.com/lefebvreperrottearthur-stack/RepoBuddy/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- ✅ Ten checks: README, usage documentation, license, `.gitignore`, contribution guide, code of conduct, security policy, GitHub Actions, tests, and basic sensitive-file-name detection
- 📊 Weighted 0–100 health score with actionable suggestions
- 🧾 Terminal, JSON and Markdown reports
- 🔒 Works completely offline: no GitHub token, external API or dependencies required at runtime
- 🧪 Automated tests and CI on Python 3.10–3.13

## Installation

Requires Python 3.10 or newer.

```bash
# In the RepoBuddy folder:
python -m pip install -e .
```

No installation is required if running directly from a cloned RepoBuddy folder:

```bash
python -m repobuddy /path/to/your/project
```

## Usage

```bash
# Inspect the current folder
repobuddy .

# Inspect another project
repobuddy /path/to/project

# Generate a Markdown report
repobuddy . --format markdown --output report.md

# Machine-readable output
repobuddy . --format json

# Fail a CI job if the score is below 80
repobuddy . --fail-under 80
```

Example output:

```text
RepoBuddy | 70/100 | 7/10 passed
========================================================
[OK] README exists
[FIX] Contribution guide exists
       -> Add CONTRIBUTING.md explaining how to contribute.
```

*Illustrative example; actual results depend on the project.*

## How scoring works

Checks are weighted by importance, for a maximum score of 100. Missing files and directories reduce the score. Sensitive-file-name matches produce a warning and reduce the score; they do **not** prove secrets were leaked. The checker does not inspect git tracking status or the actual contents of secret files. A high score is **not** a security certification.

## Development

```bash
python -m pip install -e .
```

To run the tests, install pytest and use:

```bash
python -m pip install pytest
python -m pytest -q
```

## Roadmap

- [ ] Check package manifests and dependency metadata
- [ ] Analyze README quality and broken local links
- [ ] Support custom rules in `repobuddy.toml`
- [ ] Provide an optional GitHub Action integration
- [ ] Add multilingual messages

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Beginner-friendly issues are welcome.

## Security

See [SECURITY.md](SECURITY.md). RepoBuddy is a heuristic helper, **not** a substitute for a security audit or a secret scanner.

## License

[MIT](LICENSE). Contributions are welcome.
