# Technical documentation starter

This template starts a small documentation project with a task-oriented structure and a GitHub Pages deployment workflow.

## Use it

```bash
git clone <your-repository-url> docs-site
cd docs-site
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/validate_docs.py
mkdocs build --strict
```

The `site/` directory is disposable build output. The Markdown in `docs/` and the navigation in `mkdocs.yml` are the source of truth.

## What to replace first

1. Rename `Example API` in `mkdocs.yml`.
2. Replace the placeholder command in `docs/getting-started.md` with a verified first task.
3. Add real configuration fields in `docs/reference/configuration.md`.
4. Keep failures that readers can actually encounter in `docs/troubleshooting.md`.
5. Enable GitHub Pages with **GitHub Actions** before relying on `.github/workflows/deploy.yml`.

The included validator checks that navigation targets exist, each page has a single H1, and local Markdown links resolve. It does not prove product behavior, security, accessibility, or hosting permissions.
