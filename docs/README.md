# SINAPSE SDK — website

A single-page, dependency-free starting point for the SINAPSE SDK site.
The whole thing is one file (`index.html`) with inline CSS and JS, so it's
easy to edit and build on.

## Deploy (GitHub Pages)

1. Push to `main`.
2. Repo **Settings → Pages → Build and deployment**.
3. Set **Source** to *Deploy from a branch*, branch **`main`**, folder **`/docs`**.
4. The site publishes at `https://sinapse-nsf.github.io/sinapse-sdk/`.

`.nojekyll` is included so GitHub Pages serves the files as-is (no Jekyll build).

## Editing

- **Components** — the cards and the network nodes are both generated from the
  `COMPONENTS` array near the bottom of `index.html`. Add or edit an entry
  (name, color, description, repo, url) and both update.
- **Copy** — hero, about, and footer text are plain HTML in `index.html`.
- **Colors / type** — the `:root` CSS variables at the top control the palette
  and fonts.

## Local preview

Open `index.html` in a browser, or serve the folder:

```sh
cd docs && python3 -m http.server 8000   # then visit http://localhost:8000
```
