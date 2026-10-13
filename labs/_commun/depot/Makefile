# Les étapes de la chaîne vivent ICI, dans le dépôt : la même commande tourne
# sur votre poste et dans la pipeline. Le fichier de pipeline ne fait que les
# appeler, dans l'ordre.

VERSION := $(shell sed -n 's/^__version__ = "\(.*\)"/\1/p' src/inventaire/__init__.py)
ARTEFACT := dist/inventaire-$(VERSION).pyz

.PHONY: lint test build clean version

lint:
	python3 -m pyflakes src tests

test:
	python3 -m unittest discover -s tests -v

build:
	mkdir -p dist
	python3 -m zipapp src -m 'inventaire.__main__:main' -p '/usr/bin/env python3' -o $(ARTEFACT)
	cd dist && sha256sum inventaire-$(VERSION).pyz > inventaire-$(VERSION).pyz.sha256
	@cat dist/inventaire-$(VERSION).pyz.sha256

version:
	@echo $(VERSION)

clean:
	rm -rf dist
