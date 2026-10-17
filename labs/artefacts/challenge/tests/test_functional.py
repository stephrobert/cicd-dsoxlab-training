"""Tests du lab artefacts.

On note l'ÉTAT : la cible make publish et sa pipeline sur le dépôt, la version
1.0.0 dans le registre de la forge avec son empreinte, et l'artefact retrouvé
par l'apprenant, identique octet pour octet à celui du registre.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_commun"))

from forge import (
    api,
    declencheurs,
    fichier,
    statut,
    workflows,
)

from conftest import lab_host, message

HOTE = "forge-1.lab"
VERSION = "1.0.0"
PYZ = f"inventaire-{VERSION}.pyz"


@pytest.fixture(scope="module")
def host():
    return lab_host(HOTE)


@pytest.fixture
def pipelines(host):
    return workflows(host, "main")


@pytest.fixture
def fichiers_publies(host):
    rendu = api(host, f"packages/apprenant/generic/inventaire/{VERSION}/files") or []
    return {f["name"]: f for f in rendu}


def test_cible_publish_dans_le_makefile(host):
    """La publication est une cible du dépôt, comme les autres étapes."""
    makefile = fichier(host, "Makefile") or ""
    assert re.search(r"^publish\s*:", makefile, re.M), message(
        en="The Makefile on main has no publish target.",
        fr="Le Makefile de main n'a pas de cible publish.",
    )


def test_publication_sur_etiquette_avec_secret(pipelines):
    """La pipeline publie sur une étiquette v*, avec le jeton venu d'un secret."""
    sur_etiquette = any(
        (declencheurs(d).get("push") or {}).get("tags") for d in pipelines.values()
    )
    assert sur_etiquette, message(
        en="No pipeline triggers on a tag (on: push: tags: ['v*']).",
        fr="Aucune pipeline ne se déclenche sur une étiquette (on: push: tags: ['v*']).",
    )
    textes = []
    for doc in pipelines.values():
        for job in (doc.get("jobs") or {}).values():
            for etape in job.get("steps") or []:
                if "make publish" in str(etape.get("run", "")):
                    textes.append(str(etape.get("env", {})))
    assert textes, message(
        en="No step calls make publish.",
        fr="Aucune étape n'appelle make publish.",
    )
    assert any("secrets.REGISTRE_JETON" in t for t in textes), message(
        en="The make publish step must receive REGISTRE_JETON through env: ${{ secrets.REGISTRE_JETON }}.",
        fr="L'étape make publish doit recevoir REGISTRE_JETON par env: ${{ secrets.REGISTRE_JETON }}.",
    )


def test_publication_sans_jeton_en_clair(host, pipelines):
    """La publication existe, et aucun jeton n'est écrit dans le dépôt."""
    makefile = fichier(host, "Makefile") or ""
    assert re.search(r"^publish\s*:", makefile, re.M), message(
        en="No publish target yet: nothing to check.",
        fr="Pas encore de cible publish : rien à contrôler.",
    )
    contenus = [makefile] + [str(d) for d in pipelines.values()]
    assert not any(re.search(r"\b[0-9a-f]{40}\b", c.replace("3d3c42e5aac5ba805825da76410c181273ba90b1", "")) for c in contenus), message(
        en="A 40-character hexadecimal string, a likely token, is written in the repository.",
        fr="Une chaîne de 40 caractères hexadécimaux, un jeton probable, est écrite dans le dépôt.",
    )


def test_pipeline_d_etiquette_verte(host):
    """La pipeline de l'étiquette v1.0.0 a réussi."""
    assert statut(host, f"v{VERSION}") == "success", message(
        en=f"Status of v{VERSION}: {statut(host, f'v{VERSION}') or 'none'}. Push the tag (git push origin v{VERSION}).",
        fr=f"Statut de v{VERSION} : {statut(host, f'v{VERSION}') or 'aucun'}. Poussez l'étiquette (git push origin v{VERSION}).",
    )


def test_version_publiee_avec_son_empreinte(host, fichiers_publies):
    """Le registre porte l'artefact 1.0.0 et un fichier .sha256 qui le décrit."""
    assert PYZ in fichiers_publies, message(
        en=f"{PYZ} absent from the registry (the learner account's packages).",
        fr=f"{PYZ} absent du registre (paquets du compte apprenant).",
    )
    assert f"{PYZ}.sha256" in fichiers_publies, message(
        en=f"{PYZ}.sha256 absent from the registry.",
        fr=f"{PYZ}.sha256 absent du registre.",
    )
    publie = host.check_output(
        f"curl -fsS http://localhost:3000/api/packages/apprenant/generic/inventaire/{VERSION}/{PYZ}.sha256"
    ).split()[0]
    assert publie == fichiers_publies[PYZ]["sha256"], message(
        en="The checksum published in the .sha256 does not match the registry's artefact.",
        fr="L'empreinte publiée dans le .sha256 ne correspond pas à l'artefact du registre.",
    )


def test_artefact_retrouve_par_empreinte(host, fichiers_publies):
    """~/inventaire-1.0.0.pyz est l'artefact du registre, à l'octet près."""
    local = host.file(f"/home/ansible/{PYZ}")
    assert local.exists, message(
        en=f"Download the published version into ~/{PYZ}.",
        fr=f"Téléchargez la version publiée dans ~/{PYZ}.",
    )
    assert PYZ in fichiers_publies, message(
        en="Nothing to compare: the version is not published.",
        fr="Rien à comparer : la version n'est pas publiée.",
    )
    assert local.sha256sum == fichiers_publies[PYZ]["sha256"], message(
        en="The artefact in ~ does not have the registry's checksum: it is a local rebuild, not the published artefact.",
        fr="L'artefact de ~ n'a pas l'empreinte du registre : c'est une reconstruction locale, pas l'artefact publié.",
    )
