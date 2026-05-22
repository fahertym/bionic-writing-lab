# Custom Domain

Bionic Writing Lab is set up to publish as a static Pages site on `bionicwritinglab.com` without changing the Markdown-first publishing model.

## Current Model

- `site/site.json` defines the active `base_url`: `https://bionicwritinglab.com`.
- The site builder writes `dist/site/CNAME` from that `base_url`.
- Canonical URLs, Open Graph URLs, feeds, publication indexes, search indexes, and download links use the same configured `base_url`.
- GitHub Actions builds `dist/site/`, smoke-checks the generated artifact, and deploys it with the Pages workflow.
- When deploying through a GitHub Actions Pages workflow, the repository Pages custom-domain setting still needs to be configured outside the repo; the generated `CNAME` keeps the artifact inspectable and portable.

## Outside-Repo Setup

1. Point DNS for `bionicwritinglab.com` at the active Pages host.
2. Enable `bionicwritinglab.com` in the repository or Pages project settings.
3. Verify HTTPS after DNS has propagated.
4. Optionally redirect or alias `www.bionicwritinglab.com` to `bionicwritinglab.com`.

## What Should Not Change

- Markdown remains the source of truth.
- Publication manifests remain the routing and metadata layer.
- The site stays static-host friendly.
- Adding a custom domain should not introduce a backend or service dependency.
