VERSION ?= 2.3.0

comma := ,
COMMA_VERSION := $(subst .,${comma} ,${VERSION})

QUAIL_DIR ?= ../../quail
PYTHON ?= python

# Match what actually exists in your repo (per your screenshot)
# Exclude: bin, .vscode, notes, test, wce_test unless you want them packaged.
ADDON_DIRS := bin_quail common decoder encoder exporter importer logger material_panel panels script ui view_panel wce

.PHONY: test build build-darwin
test:
	@pytest --rootdir=. wce/wce_test.py

build:
	@echo "build: packing and building"
	mkdir -p bin
	-rm -rf bin/*

	# Build and bundle helper exe
	cd $(QUAIL_DIR) && make build-windows-addon
	cp $(QUAIL_DIR)/bin/quail-addon.exe bin/quail.exe

	# Patch versions / build flags
	$(PYTHON) -c "from pathlib import Path; p=Path('__init__.py'); t=p.read_text(encoding='utf-8'); t=t.replace('\"version\": (1, 0, 0),','\"version\": ($(COMMA_VERSION)),'); p.write_text(t, encoding='utf-8')"
	$(PYTHON) -c "from pathlib import Path; p=Path('common/__init__.py'); t=p.read_text(encoding='utf-8'); t=t.replace('\"0.0.1\"','\"$(VERSION)\"'); t=t.replace('return True  # Build','return False  # Build'); p.write_text(t, encoding='utf-8')"

	# Stage addon files
	mkdir -p bin/quail_addon
	cp bin/quail.exe LICENSE README.md *.py bin/quail_addon

	# IMPORTANT: include the Blender Extensions manifest if present
	@if [ -f blender_manifest.toml ]; then cp blender_manifest.toml bin/quail_addon; else echo "WARN: blender_manifest.toml missing in repo root"; fi

	# Copy addon directories (only if they exist)
	@for d in $(ADDON_DIRS); do \
		if [ -d "$$d" ]; then cp -r "$$d" bin/quail_addon; else echo "skip: $$d (missing)"; fi; \
	done

	# Create zip using Python (no external zip dependency)
	$(PYTHON) -c "import os, zipfile; root='bin/quail_addon'; out='bin/quail-$(VERSION).zip'; z=zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED); \
	[dn.remove('__pycache__') for dp,dn,fn in os.walk(root) if '__pycache__' in dn]; \
	[None for dp,dn,fn in os.walk(root) for f in fn if not f.endswith(('.pyc','.pyo')) and (lambda p,arc: z.write(p,arc))(os.path.join(dp,f), os.path.relpath(os.path.join(dp,f),'bin'))]; \
	z.close()"

	# Cleanup staging
	rm -rf bin/quail_addon
	rm -f bin/quail.exe

	# Revert patched files back to dev defaults
	$(PYTHON) -c "from pathlib import Path; p=Path('__init__.py'); t=p.read_text(encoding='utf-8'); t=t.replace('\"version\": ($(COMMA_VERSION)),','\"version\": (1, 0, 0),'); p.write_text(t, encoding='utf-8')"
	$(PYTHON) -c "from pathlib import Path; p=Path('common/__init__.py'); t=p.read_text(encoding='utf-8'); t=t.replace('return False  # Build','return True  # Build'); t=t.replace('\"$(VERSION)\"','\"0.0.1\"'); p.write_text(t, encoding='utf-8')"

build-darwin:
	@echo "build-darwin: packing and building"
	@mkdir -p bin
	cd $(QUAIL_DIR) && make build-darwin
	cp $(QUAIL_DIR)/bin/quail-darwin quail-darwin