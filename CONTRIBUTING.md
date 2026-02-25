# Contributing to pyodoo-rpc-client

Thanks for your interest in improving `pyodoo-rpc-client`.

## How to engage

- Use **Issues** for bugs and concrete feature requests.
- Use **Discussions** (if enabled in GitHub settings) for open-ended questions, compatibility advice, and design conversations.
- Open **Pull Requests** for focused fixes and enhancements.

## Project scope

- This repository targets the Odoo legacy RPC API for Odoo v19 and below.
- For the Odoo JSON 2 API (v19+ compliant), refer to `pyodoo-client`.

## Before opening an Issue

- Search existing Issues first.
- Use the appropriate Issue template.
- For bugs, include environment, reproduction steps, expected behavior, and actual behavior.

## Pull Request process

1. Fork the repository.
2. Create a branch from your target base branch.
3. Keep the change focused and minimal.
4. Update documentation if behavior or public API changed.
5. Run packaging checks:
   - `python -m build`
   - `python -m twine check dist/*`
6. Open a PR and complete the template.

## Review expectations

- Keep commit messages clear.
- Link related Issues in PR descriptions (for example: `Fixes #123`).
- Respond to review comments and push updates as needed.
