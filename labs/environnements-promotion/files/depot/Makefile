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

# --- Publication ---------------------------------------------------------------
# Le registre de paquets de la forge. Le jeton vient de l'ENVIRONNEMENT
# (secret de la pipeline), jamais du dépôt.
REGISTRE := http://localhost:3000/api/packages/apprenant/generic/inventaire

.PHONY: publish
publish:
	@test -f $(ARTEFACT) || { echo "Aucun artefact : lancez d'abord make build"; exit 1; }
	@test -n "$$REGISTRE_JETON" || { echo "REGISTRE_JETON absent de l'environnement"; exit 1; }
	@test "$${GITHUB_REF_NAME:-v$(VERSION)}" = "v$(VERSION)" || { echo "L'étiquette $$GITHUB_REF_NAME ne correspond pas à la version $(VERSION)"; exit 1; }
	curl --fail-with-body --silent --show-error --user "apprenant:$$REGISTRE_JETON" \
	  --upload-file $(ARTEFACT) $(REGISTRE)/$(VERSION)/inventaire-$(VERSION).pyz
	curl --fail-with-body --silent --show-error --user "apprenant:$$REGISTRE_JETON" \
	  --upload-file $(ARTEFACT).sha256 $(REGISTRE)/$(VERSION)/inventaire-$(VERSION).pyz.sha256
	@echo "Publié : inventaire $(VERSION)"

# --- Déploiement ----------------------------------------------------------------
# Installe une version DÉJÀ publiée ; ne construit rien.
#   make deployer ENV=recette VERSION=1.1.0
#   make deployer ENV=production VERSION=1.1.0 EMPREINTE=<empreinte relevée en recette>
# Les valeurs passent au script par l'ENVIRONNEMENT : make ne les recolle pas
# dans la ligne de commande, le shell ne peut donc pas les réinterpréter.
.PHONY: deployer
deployer: export DEPLOI_ENV := $(ENV)
deployer: export DEPLOI_VERSION := $(VERSION)
deployer: export DEPLOI_EMPREINTE := $(EMPREINTE)
deployer:
	./scripts/deployer.sh "$$DEPLOI_ENV" "$$DEPLOI_VERSION" "$$DEPLOI_EMPREINTE"
