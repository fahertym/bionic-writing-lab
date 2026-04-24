PYTHON ?= $(shell if [ -x .venv/bin/python ]; then printf .venv/bin/python; else printf python3; fi)
PORT ?= 8000

.PHONY: validate site downloads build clean serve

validate:
	$(PYTHON) scripts/validate_publications.py

site:
	$(PYTHON) scripts/build_site.py

downloads:
	$(PYTHON) scripts/export_downloads.py

build: validate site downloads

clean:
	rm -rf dist/site dist/build
	mkdir -p dist
	touch dist/.gitkeep

serve:
	$(PYTHON) -m http.server $(PORT) --directory dist/site
