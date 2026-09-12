# Contributing to BootBridge

Thank you for your interest in contributing to **BootBridge**! We welcome contributions from developers of all skill levels.

## How to Contribute

### 1. Reporting Bugs
Before creating a bug report, please check existing issues. If you find a new bug, open an issue including:
- OS Version & Host Linux Distribution
- Physical Drive Type (NVMe / SATA SSD / HDD)
- QEMU / OVMF Version (`qemu-system-x86_64 --version`)
- Console Logs output from BootBridge live diagnostics

### 2. Feature Requests
Open a GitHub Issue detailing:
- The problem your feature solves
- Proposed technical implementation or UI changes

### 3. Submitting Pull Requests
1. Fork the repository on GitHub.
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes following Conventional Commits format (`feat: ...`, `fix: ...`, `docs: ...`).
4. Ensure code passes syntax check: `python3 -m py_compile bootbridge.py core/*.py`
5. Push to your branch and submit a Pull Request.

## Code Style
- Write clean Python 3 code conforming to PEP 8 standards.
- Maintain error logging via `self.log_callback`.
- Keep safety checks in `core/safety_checker.py` robust and non-destructive.
