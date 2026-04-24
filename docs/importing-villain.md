# Importing Villain Later

This document describes the intended future import path for `villain-in-the-verse` without importing that project yet.

## Current Boundary

- `/home/matt/docs/villain-in-the-verse` remains its own content and project repository.
- `/home/matt/docs/bionic-writing-lab` is the publishing layer.
- The Villain repo should not be mutated by work in this repo.

## Intended Approach

When the time comes to bring Villain into Bionic Writing Lab:

1. Export or copy Markdown source into `content/books/villain-in-the-verse/`.
2. Keep Markdown as the source of truth inside this repo as well.
3. Add a manifest such as `publications/villain-in-the-verse.json`.
4. Define the web route, output formats, and metadata in the manifest instead of carrying over repo-specific build logic.
5. Reuse only general publishing concepts from the Villain repo, not Villain-specific assumptions.

## What To Avoid

- Do not import Villain-specific build commands as mandatory architecture.
- Do not hard-code trilogy, chapter-management, or project naming assumptions into Bionic Writing Lab.
- Do not make Bionic Writing Lab depend on the Villain repo at runtime.

## Long-Term Possibility

If a sync workflow is ever needed, it should move Markdown and metadata into this repo in a predictable way while keeping the publishing system generic and inspectable.

