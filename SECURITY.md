# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |
| < 0.2   | No        |

## Reporting a Vulnerability

If you find a security issue in GideonSTEM-Maschine, **please do not open a public GitHub issue.**

Instead, report it privately:

1. Go to the [Security Advisories](https://github.com/gbroeckling/GideonSTEM-Maschine/security/advisories) page
2. Click **"Report a vulnerability"**
3. Describe the issue and how to reproduce it

You should receive a response within 7 days. If the issue is confirmed, a fix will be released as soon as practical and you will be credited in the changelog (unless you prefer to remain anonymous).

## Scope

This project is a Python build that generates Traktor `.tsi` and NI Controller Editor
`.ncc` files. Relevant concerns:

- Path traversal or arbitrary file write in `build_gideonStemsMaster.py`,
  `make_layout.py`, or `annotate_template.py`.
- Any committed secret, credential, or session token (none should ever be present — see below).

## What Doesn't Count

- The generated `.tsi` / `.ncc` are MIDI mapping **data** — they contain no executable code.
- Issues requiring physical access to your machine or DJ hardware.
- The mapping doing something unexpected in Traktor (that's a bug, not a security issue —
  open a normal issue).

## Security Measures Already in Place

- **No secrets in the repo.** A *whitelist* `.gitignore` allows only known-good source,
  docs, and build outputs. The authenticated DJTechTools session (`djtt/`, cookies),
  third-party reference mappings (`decode/`, `*.bin`, vendor `.tsi`), and all working
  artifacts are excluded by default — nothing is committed unless explicitly allowed.
- **Secret-scanning push protection** is enabled on the repository.
- The build is fully self-contained: it reads only its own committed files and makes no
  network calls.
