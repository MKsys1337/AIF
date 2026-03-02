# Security Policy

## Supported Versions

| Package | Version | Supported |
|---------|---------|-----------|
| aif-core (Python) | 0.1.x | Yes |
| @aif/renderer (JS) | 0.1.x | Yes |
| AIF (Swift) | 0.1.x | Yes |

## Reporting a Vulnerability

If you discover a security vulnerability in AIF, please report it responsibly.

**Do not open a public GitHub issue.**

Instead, send an email to: **support@mkhub.de**

Please include:

- Description of the vulnerability
- Steps to reproduce
- Affected package(s) and version(s)
- Potential impact

## Response Timeline

- **Acknowledgment**: within 48 hours
- **Initial assessment**: within 7 days
- **Fix and disclosure**: coordinated with the reporter

## Scope

The following are in scope:

- Image processing vulnerabilities (buffer overflows, out-of-bounds reads)
- XMP injection or metadata manipulation
- Client-side rendering exploits (XSS via image metadata)
- Dependency vulnerabilities in direct dependencies

## Security Considerations

AIF processes user-uploaded images, which is inherently security-sensitive. The pipeline includes:

- Image decoding (via Pillow/OpenCV) — always use the latest patched versions
- XMP metadata embedding — sanitized to prevent injection
- Client-side Canvas operations — scoped to same-origin images (CORS)
- No arbitrary code execution — all transformations are deterministic pixel operations

Thank you for helping keep AIF secure.
