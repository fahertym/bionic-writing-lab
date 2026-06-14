# Bionic Writing Lab as the Writing Forge

This repo is now the single place to **write, publish, and deploy** — one forge for
every kind of writing. This note explains the model, how the Villain book moves in,
and the day-to-day commands.

Run everything below from the repo root with the virtualenv active:

```bash
source .venv/bin/activate    # uses the Jinja2 + Markdown deps already installed
```

---

## The model

- **Bionic = the forge.** Markdown in `content/` is canonical. Each piece has a
  manifest in `publications/*.json`. `build_site.py` renders the whole site to
  `dist/site`, and GitHub Pages publishes it on push.
- **Villain repo = left untouched for now.** Its `villain_cli`/Makefile build is
  *not* adopted — Bionic's `build_site.py` is the canonical publisher, and pulling a
  book-only build in would duplicate a weaker one. The book's *content* moves here;
  the old repo stays as origin/history until you decide its fate.
- **What we did adopt** from Villain are the authoring ergonomics Bionic lacked:
  a live preview server and a word-count/progress tool (below).

### Drafts vs. published

`status: "draft"` keeps a publication **out of the public build** but visible in
local preview. When the book is finished, change its manifest to
`"status": "published"` and the next deploy puts it live. Nothing unfinished ships
by accident.

---

## Moving the Villain book in (one-time)

The manifest is already written (status `draft`, chapters in correct reading order,
linked to the five existing Villain fragments), but **parked as
`publications/villain-in-the-verse.json.pending`** so it stays out of the `*.json`
glob and doesn't break the site build before its content exists. It expects the
manuscript at `content/books/villain-in-the-verse/`. When you're ready (after the
scripture migration is further along), activate it and copy the chapters in with a
byte-exact `cp` (the manuscript is left as the source of truth — no editing):

```bash
mv publications/villain-in-the-verse.json.pending publications/villain-in-the-verse.json
mkdir -p content/books/villain-in-the-verse
cp -r ../villain-in-the-verse/publications/book1/manuscript/. content/books/villain-in-the-verse/
```

Then verify:

```bash
python scripts/validate_publications.py
python scripts/stats.py --publication villain-in-the-verse
python scripts/preview.py        # open http://localhost:8000/books/villain-in-the-verse/
```

`validate_publications.py` will report errors for the book manifest **until** the
copy step is done (its source folder won't exist yet). That's expected.

> Resync later only matters if you keep editing in the Villain repo. Re-running the
> same `cp -r` overwrites the copies. Once you're writing here in Bionic, the book
> lives here and there's nothing to sync.

---

## Day-to-day commands

| Task | Command |
| --- | --- |
| Live preview while writing (drafts visible) | `python scripts/preview.py` |
| Preview exactly what ships publicly | `python scripts/preview.py --public` |
| Word counts + progress to target for everything | `python scripts/stats.py` |
| Progress on just the book | `python scripts/stats.py --publication villain-in-the-verse` |
| Validate all manifests | `python scripts/validate_publications.py` |
| Build the public site | `python scripts/build_site.py` |
| Import a new piece from a Markdown file/folder | `python scripts/import_markdown.py --source <path> --kind <kind>` |
| Scaffold a new publication | `python scripts/new_publication.py` |

`target_words` is an optional manifest field (the book sets `80000`); `stats.py`
turns it into a `47k of 80k` progress bar.

---

## Deploying (GitHub Pages)

A workflow at `.github/workflows/deploy.yml` builds `dist/site` and publishes to
Pages on every push to `main`. One-time setup:

1. GitHub repo → **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. `site/site.json` `base_url` is `https://bionicwritinglab.com`, so the build emits
   a `CNAME`. Point that domain's DNS at GitHub Pages and set it as the custom domain
   under Settings → Pages.
3. Push to `main`. The Actions run builds and deploys.

**Switching to Cloudflare Pages later:** the deployable artifact is always
`dist/site/`. In Cloudflare Pages, set build command `python scripts/build_site.py`
and output directory `dist/site`. No code changes needed.
