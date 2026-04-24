# Custom Domain Plan

Bionic Writing Lab is currently set up to publish as a static GitHub Pages site. A custom domain can be added later without changing the Markdown-first publishing model.

## Current Model

- `site/site.json` defines the active `base_url`.
- GitHub Actions builds `dist/site/` and deploys it with the Pages workflow.
- The published site can live at the default GitHub Pages URL until a custom domain is ready.

## When A Domain Is Ready

1. Choose the canonical domain, such as `bionicwritinglab.com` or `www.bionicwritinglab.com`.
2. Update `site/site.json` so `base_url` matches the chosen domain.
3. Add a `CNAME` file during the build or workflow so the Pages artifact declares the custom host.
4. Point DNS at GitHub Pages using the records GitHub requires for the chosen root domain or subdomain.
5. Enable the custom domain in the repository Pages settings.
6. Verify HTTPS and canonical routing after DNS has propagated.

## What Should Not Change

- Markdown remains the source of truth.
- Publication manifests remain the routing and metadata layer.
- The site stays static-host friendly.
- Adding a custom domain should not introduce a backend or service dependency.

## Suggested Future Follow-Up

When the real domain is known, add a small build step that writes `dist/site/CNAME` from site config so the deploy pipeline stays reproducible.

