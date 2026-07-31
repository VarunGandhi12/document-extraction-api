# Security Policy

## Reporting a vulnerability

Please **do not** open a public issue for security problems. Report privately
via [GitHub Security Advisories](../../security/advisories/new) or by email to
the maintainer. You'll get an acknowledgement within 72 hours.

## Handling of uploaded files

- Files are parsed **in memory** and never written to disk by the service.
- Uploads above the configured size limit are rejected before parsing.
- No document content is logged — only content types and byte sizes.
- The container runs as a non-root user.

## Supported versions

The latest minor release on `main` receives security fixes.
