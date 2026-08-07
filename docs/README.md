# SINAPSE SDK — documentation

Sphinx documentation for the SINAPSE SDK, written in MyST markdown and
built with the Read the Docs theme.

## Layout

- `index.md` — project aims and installation
- `components.md` — the SDK components
- `examples.md` — component integration examples
- `conf.py` — Sphinx configuration
- `requirements.txt` — build dependencies

## Building locally

```sh
pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
open docs/_build/html/index.html
```

## Hosting

- `.readthedocs.yaml` at the repo root configures builds on
  [Read the Docs](https://readthedocs.org/) (import the repo there to
  activate it).
- `.github/workflows/deploy-pages.yml` also builds and publishes the
  docs to GitHub Pages on every push to `main`.
