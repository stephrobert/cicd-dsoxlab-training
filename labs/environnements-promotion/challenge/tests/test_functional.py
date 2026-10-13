"""Tests du lab environnements-promotion.

On note l'ÉTAT : la pipeline de déploiement à la demande, le journal des
déploiements écrit par scripts/deployer.sh, les artefacts installés dans
chaque environnement comparés au registre, et ce que chaque environnement
répond sur /version.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_commun"))

from conftest import lab_host  # noqa: E402
from forge import api, declencheurs, etapes_run, workflows  # noqa: E402

HOTE = "forge-1.lab"
JOURNAL = "/var/log/inventaire/deploiements.log"


@pytest.fixture(scope="module")
def host():
    return lab_host(HOTE)


@pytest.fixture
def empreintes(host):
    rendu = {}
    for v in ("1.0.0", "1.1.0"):
        fichiers = api(host, f"packages/apprenant/generic/inventaire/{v}/files") or []
        rendu[v] = next((f["sha256"] for f in fichiers if f["name"] == f"inventaire-{v}.pyz"), None)
    return rendu


@pytest.fixture
def deploiements(host):
    contenu = host.file(JOURNAL).content_string if host.file(JOURNAL).exists else ""
    return [ligne.split() for ligne in contenu.splitlines() if len(ligne.split()) >= 4]


def _dispatch(pipelines):
    for nom, doc in pipelines.items():
        if "workflow_dispatch" in declencheurs(doc):
            return nom, doc
    return None, None


def test_pipeline_de_deploiement_a_la_demande(host):
    """Une pipeline workflow_dispatch prend l'environnement et la version en entrée."""
    nom, doc = _dispatch(workflows(host, "main"))
    assert doc, "Aucune pipeline ne se déclenche à la demande (on: workflow_dispatch) sur main."
    entrees = (declencheurs(doc).get("workflow_dispatch") or {}).get("inputs") or {}
    assert len(entrees) >= 2, f"{nom} doit demander l'environnement et la version (inputs)."
    commandes = etapes_run(doc)
    assert any("make deployer" in c for c in commandes), f"{nom} n'appelle pas make deployer."
    assert not any("${{" in c for c in commandes), (
        "Une entrée est interpolée directement dans run: ; passez-la par env: pour éviter l'injection."
    )


def test_promotion_sans_reconstruction(deploiements, empreintes):
    """1.1.0 déployée en recette, puis la MÊME empreinte déployée en production."""
    recette = [i for i, d in enumerate(deploiements) if d[1] == "recette" and d[2] == "1.1.0"]
    assert recette, "Aucun déploiement de 1.1.0 en recette dans le journal."
    premier = recette[0]
    prod = [i for i, d in enumerate(deploiements) if i > premier and d[1] == "production" and d[2] == "1.1.0"]
    assert prod, "1.1.0 n'a pas été promue en production après la recette."
    assert deploiements[prod[0]][3] == deploiements[premier][3] == empreintes["1.1.0"], (
        "La production n'a pas reçu l'artefact de la recette, à l'empreinte près."
    )
    assert deploiements[prod[0]][4:] == ["empreinte-imposee"], (
        "La promotion doit imposer l'empreinte relevée en recette (entrée empreinte du workflow), "
        "pas seulement le numéro de version."
    )


def test_retour_arriere_en_production(deploiements):
    """Après la promotion de 1.1.0, la production est revenue à 1.0.0."""
    prod_110 = [i for i, d in enumerate(deploiements) if d[1] == "production" and d[2] == "1.1.0"]
    assert prod_110, "Pas encore de promotion de 1.1.0 en production."
    retour = [i for i, d in enumerate(deploiements) if i > prod_110[0] and d[1] == "production" and d[2] == "1.0.0"]
    assert retour, "Aucun retour arrière de la production vers 1.0.0 après la promotion."


def test_artefacts_installes(host, empreintes):
    """Chaque environnement porte l'artefact du registre, installé par le runner."""
    for env, version in (("recette", "1.1.0"), ("production", "1.0.0")):
        f = host.file(f"/opt/inventaire/{env}/inventaire.pyz")
        assert f.exists, f"Aucun artefact en {env}."
        assert f.sha256sum == empreintes[version], f"L'artefact de {env} n'est pas la version {version} du registre."
        assert f.user == "runner", f"L'artefact de {env} n'a pas été installé par la pipeline (propriétaire {f.user})."


def test_chaque_environnement_garde_sa_configuration(host):
    """Le même code répond avec la configuration de son environnement."""
    for env, port, version in (("recette", 8081, "1.1.0"), ("production", 8082, "1.0.0")):
        res = host.run(f"curl -fsS http://127.0.0.1:{port}/version")
        assert res.rc == 0, f"{env} ne répond pas sur le port {port}."
        rendu = json.loads(res.stdout)
        assert rendu == {"version": version, "environnement": env}, f"{env} répond {rendu}."
