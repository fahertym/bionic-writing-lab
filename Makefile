PYTHON ?= $(shell if [ -x .venv/bin/python ]; then printf .venv/bin/python; else printf python3; fi)
PORT ?= 8000

.PHONY: validate site downloads build smoke clean serve new import site-drafts downloads-drafts build-drafts

new:
	@if [ -z "$(kind)" ] || [ -z "$(title)" ]; then \
		echo 'Usage: make new kind=essay title="My New Essay"'; \
		exit 1; \
	fi
	$(PYTHON) scripts/new_publication.py --kind "$(kind)" --title "$(title)" $(if $(subtitle),--subtitle "$(subtitle)") $(if $(description),--description "$(description)") $(if $(slug),--slug "$(slug)") $(if $(author),--author "$(author)") $(if $(status),--status "$(status)") $(if $(tags),--tags "$(tags)") $(if $(formats),--formats "$(formats)")

import:
	@if [ -z "$(source)" ] || [ -z "$(kind)" ]; then \
		echo 'Usage: make import source=/path/to/file.md kind=essay'; \
		exit 1; \
	fi
	$(PYTHON) scripts/import_markdown.py --source "$(source)" --kind "$(kind)" $(if $(title),--title "$(title)") $(if $(subtitle),--subtitle "$(subtitle)") $(if $(description),--description "$(description)") $(if $(slug),--slug "$(slug)") $(if $(author),--author "$(author)") $(if $(status),--status "$(status)") $(if $(tags),--tags "$(tags)") $(if $(formats),--formats "$(formats)") $(if $(filter 1 true yes,$(dry_run)),--dry-run)

validate:
	$(PYTHON) scripts/validate_publications.py

site:
	$(PYTHON) scripts/build_site.py

site-drafts:
	INCLUDE_DRAFTS=1 $(PYTHON) scripts/build_site.py

downloads:
	$(PYTHON) scripts/export_downloads.py

downloads-drafts:
	INCLUDE_DRAFTS=1 $(PYTHON) scripts/export_downloads.py

build: validate site downloads

build-drafts: validate site-drafts downloads-drafts

smoke:
	$(PYTHON) scripts/smoke_check.py

clean:
	rm -rf dist/site dist/build
	mkdir -p dist
	touch dist/.gitkeep

serve:
	$(PYTHON) -m http.server $(PORT) --directory dist/site
