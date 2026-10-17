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

from forge import api, declencheurs, etapes_run, workflows

from conftest import lab_host, message

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
    assert doc, message(
        en="No pipeline triggers on demand (on: workflow_dispatch) on main.",
        fr="Aucune pipeline ne se déclenche à la demande (on: workflow_dispatch) sur main.",
    )
    entrees = (declencheurs(doc).get("workflow_dispatch") or {}).get("inputs") or {}
    assert len(entrees) >= 2, message(
        en=f"{nom} must ask for the environment and the version (inputs).",
        fr=f"{nom} doit demander l'environnement et la version (inputs).",
    )
    commandes = etapes_run(doc)
    assert any("make deployer" in c for c in commandes), message(
        en=f"{nom} does not call make deployer.",
        fr=f"{nom} n'appelle pas make deployer.",
    )
    assert not any("${{" in c for c in commandes), message(
        en="An input is interpolated directly into run:; pass it through env: to avoid injection.",
        fr="Une entrée est interpolée directement dans run: ; passez-la par env: pour éviter l'injection.",
    )
    for c in commandes:
        if "make deployer" in c:
            assert "=" not in c, message(
                en=f"Values passed on make's command line ({c}): make would expand them. "
                "Pass DEPLOI_ENV, DEPLOI_VERSION and DEPLOI_EMPREINTE through env:.",
                fr=f"Valeurs passées sur la ligne de commande de make ({c}) : make les développerait. "
                "Passez DEPLOI_ENV, DEPLOI_VERSION et DEPLOI_EMPREINTE par env:.",
            )


def test_promotion_sans_reconstruction(deploiements, empreintes):
    """1.1.0 déployée en recette, puis la MÊME empreinte déployée en production."""
    recette = [i for i, d in enumerate(deploiements) if d[1] == "recette" and d[2] == "1.1.0"]
    assert recette, message(
        en="No deployment of 1.1.0 to staging in the log.",
        fr="Aucun déploiement de 1.1.0 en recette dans le journal.",
    )
    premier = recette[0]
    prod = [i for i, d in enumerate(deploiements) if i > premier and d[1] == "production" and d[2] == "1.1.0"]
    assert prod, message(
        en="1.1.0 was not promoted to production after staging.",
        fr="1.1.0 n'a pas été promue en production après la recette.",
    )
    assert deploiements[prod[0]][3] == deploiements[premier][3] == empreintes["1.1.0"], message(
        en="Production did not receive staging's artefact, down to the checksum.",
        fr="La production n'a pas reçu l'artefact de la recette, à l'empreinte près.",
    )
    assert deploiements[prod[0]][4:] == ["empreinte-imposee"], message(
        en="The promotion must enforce the checksum recorded in staging (the workflow's "
        "empreinte input), not only the version number.",
        fr="La promotion doit imposer l'empreinte relevée en recette (entrée empreinte du workflow), "
        "pas seulement le numéro de version.",
    )


def test_retour_arriere_en_production(deploiements):
    """Après la promotion de 1.1.0, la production est revenue à 1.0.0."""
    prod_110 = [i for i, d in enumerate(deploiements) if d[1] == "production" and d[2] == "1.1.0"]
    assert prod_110, message(
        en="No promotion of 1.1.0 to production yet.",
        fr="Pas encore de promotion de 1.1.0 en production.",
    )
    retour = [i for i, d in enumerate(deploiements) if i > prod_110[0] and d[1] == "production" and d[2] == "1.0.0"]
    assert retour, message(
        en="No rollback of production to 1.0.0 after the promotion.",
        fr="Aucun retour arrière de la production vers 1.0.0 après la promotion.",
    )


def test_artefacts_installes(host, empreintes):
    """Chaque environnement porte l'artefact du registre, installé par le runner."""
    for env, version in (("recette", "1.1.0"), ("production", "1.0.0")):
        f = host.file(f"/opt/inventaire/{env}/inventaire.pyz")
        assert f.exists, message(
            en=f"No artefact in {env}.",
            fr=f"Aucun artefact en {env}.",
        )
        assert f.sha256sum == empreintes[version], message(
            en=f"The artefact of {env} is not version {version} from the registry.",
            fr=f"L'artefact de {env} n'est pas la version {version} du registre.",
        )
        assert f.user == "runner", message(
            en=f"The artefact of {env} was not installed by the pipeline (owner {f.user}).",
            fr=f"L'artefact de {env} n'a pas été installé par la pipeline (propriétaire {f.user}).",
        )


def test_chaque_environnement_garde_sa_configuration(host):
    """Le même code répond avec la configuration de son environnement."""
    for env, port, version in (("recette", 8081, "1.1.0"), ("production", 8082, "1.0.0")):
        res = host.run(f"curl -fsS http://127.0.0.1:{port}/version")
        assert res.rc == 0, message(
            en=f"{env} does not answer on port {port}.",
            fr=f"{env} ne répond pas sur le port {port}.",
        )
        rendu = json.loads(res.stdout)
        assert rendu == {"version": version, "environnement": env}, message(
            en=f"{env} answers {rendu}.",
            fr=f"{env} répond {rendu}.",
        )
