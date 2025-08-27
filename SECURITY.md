# Security Policy

Thank you for helping keep this project and its users safe.

## Supported Versions

- Active development branch (default) and the latest minor release receive security fixes.
- Older versions may not receive patches; please upgrade to the latest release.

## Reporting a Vulnerability

Please report vulnerabilities privately. Do not open a public issue.

- Preferred: Open a private GitHub Security Advisory for this repository.
- Alternative: Email the maintainers at [longreader@brzv.sk]
  with details and a way to reproduce.

What to include:
- Affected component(s) and version/commit if known
- Reproduction steps, proof-of-concept, or crash logs
- Impact assessment (what can an attacker do?)
- Your suggested remediation, if any

We will acknowledge receipt within 3 business days and provide an initial
assessment within 7 business days. We strive to fix critical issues quickly
and will coordinate disclosure with you. If you prefer attribution upon
disclosure, please let us know.

## Safe Harbor

We consider activities consistent with this policy to be authorized in good
faith research. Please avoid privacy violations, data destruction, service
disruption, and exfiltration of more data than necessary to demonstrate an
issue.

## PGP/Key (optional)

If you require encrypted communication, please share your PGP key or request
one from the maintainers.

## Key and Permission Guidance

- Telegram Bot: use a bot token created for this project only. Restrict access
  to maintainers. Rotate if exposed. No additional scopes are configurable.
- Database: provision a database user with least privileges required by the
  application (read/write to the app database only). Avoid admin/root users in
  production.
- Third-party APIs (e.g., text-to-speech providers): create per-env API keys
  with minimal scopes and rate limits where available. Do not reuse personal
  accounts.

