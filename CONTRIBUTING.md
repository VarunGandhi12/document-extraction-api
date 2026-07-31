# Contributing

Thanks for taking a look. This project is intentionally small and well-tested;
contributions should keep it that way.

## Getting started

```bash
python -m venv .venv && source .venv/bin/activate
make install          # editable install with dev extras
make test             # run the suite with coverage
make run              # http://localhost:8000/docs
```

## Before you open a PR

- `make lint` · `make format` · `make typecheck` · `make test` all pass.
- New behaviour comes with tests. Coverage gate is **85%**.
- Commits follow [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`).

## Architecture in one line

`API (routes) → ExtractionService → ParserRegistry → Parser → Normalizer`.
Add a file type by writing a `Parser` and registering it — nothing else changes.

## Adding a parser

1. Implement the `Parser` protocol in `app/parsers/`.
2. Register it in `app/parsers/registry.py`.
3. Add unit tests for the parser and an integration test with a generated fixture.
