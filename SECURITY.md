# Security Policy for hermes-sync

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.0   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in hermes-sync, please report it responsibly.

### How to Report

1. **Do NOT create a public issue** — this would expose the vulnerability
2. **Email us directly**: ia.creative.tn@gmail.com
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes (optional)

### What to Expect

- We will acknowledge your report within 7 days
- We will investigate and respond within 14 days
- We will keep you informed of progress
- We will credit you in the release notes (if you wish)

### Security Considerations

**Already documented in README:**
- Use a strong passphrase for encrypting secrets
- Keep your Git remote private (or use encrypted secrets if public)
- Rotate credentials if accidentally synced unencrypted
- The passphrase is never stored — only provided via environment variable

---

*Hermes-sync is an unofficial companion tool, not affiliated with Nous Research.*