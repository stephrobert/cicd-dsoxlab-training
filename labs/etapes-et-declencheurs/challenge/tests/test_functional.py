"""Tests du lab etapes-et-declencheurs.

On note l'ÉTAT laissé sur la forge et sur la machine :

- un fichier de pipeline existe sur main, déclenché par un push sur main et
  par une demande de fusion, et il n'appelle QUE des cibles make ;
- la pipeline est verte sur le dernier commit de main ;
- une demande de fusion porte un commit dont la pipeline est rouge ;
- l'échec a été reproduit en local, sortie conservée dans ~/echec-local.txt.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_commun"))

from conftest import lab_host  # noqa: E402
from forge import DEPOT, api, declencheurs, etapes_run, fichier, statut, workflows  # noqa: E402

HOTE = "forge-1.lab"


@pytest.fixture(scope="module")
def host():
    return lab_host(HOTE)


@pytest.fixture
def pipelines(host):
    return workflows(host, "main")


def test_pipeline_sur_main(pipelines):
    """Un fichier de pipeline existe dans .forgejo/workflows/ sur main."""
    assert pipelines, (
        "Aucun fichier .yml dans .forgejo/workflows/ sur la branche main : "
        "écrivez la pipeline, commitez-la et poussez-la (git push origin main)."
    )
    assert not any(d.get("__invalide__") for d in pipelines.values()), "Un fichier de pipeline n'est pas du YAML valide."


def test_declencheurs_push_et_demande_de_fusion(pipelines):
    """La pipeline se déclenche sur un push vers main et sur une demande de fusion."""
    ok_push = ok_pr = False
    for doc in pipelines.values():
        on = declencheurs(doc)
        if "push" in on:
            branches = (on.get("push") or {}).get("branches")
            ok_push = ok_push or branches is None or "main" in branches
        ok_pr = ok_pr or "pull_request" in on
    assert ok_push, "Aucune pipeline ne se déclenche sur un push vers main (on: push: branches: [main])."
    assert ok_pr, "Aucune pipeline ne se déclenche sur une demande de fusion (on: pull_request)."


def test_cible_lint_ecrite(host):
    """Le Makefile de main porte la cible lint, écrite par l'apprenant."""
    makefile = fichier(host, "Makefile") or ""
    assert re.search(r"^lint\s*:", makefile, re.M), "Le Makefile de main n'a pas de cible lint."
    assert "pyflakes" in makefile, "La cible lint doit lancer pyflakes (python3 -m pyflakes src tests)."


def test_la_pipeline_n_appelle_que_make(pipelines):
    """Les étapes vivent dans le Makefile : chaque `run:` appelle une cible make."""
    commandes = [c for doc in pipelines.values() for c in etapes_run(doc)]
    assert commandes, "La pipeline n'a aucune étape run:."
    for cible in ("lint", "test", "build"):
        assert any(f"make {cible}" in c for c in commandes), f"La pipeline n'appelle pas make {cible}."
    hors_make = [c for c in commandes if not all(ligne.strip().startswith("make") for ligne in c.splitlines() if ligne.strip())]
    assert not hors_make, (
        "Ces étapes font autre chose qu'appeler make : "
        f"{hors_make}. Déplacez la commande dans une cible du Makefile, pour qu'elle tourne pareil en local."
    )


def test_pipeline_verte_sur_main(host):
    """Le dernier commit de main porte une pipeline réussie."""
    etat = statut(host, "main")
    assert etat == "success", (
        f"Statut de main : {etat or 'aucun'}. Attendez la fin de la pipeline (onglet Actions), "
        "ou corrigez l'étape qui échoue."
    )


def test_demande_de_fusion_rouge(host):
    """Une demande de fusion ouverte porte un commit dont la pipeline échoue."""
    demandes = api(host, f"repos/{DEPOT}/pulls?state=open") or []
    assert demandes, "Aucune demande de fusion ouverte : poussez une branche avec un test cassé et ouvrez-en une."
    etats = [statut(host, d["head"]["sha"]) for d in demandes]
    assert "failure" in etats, (
        f"Statuts des demandes de fusion : {etats}. La pipeline doit échouer sur le test cassé."
    )


def test_echec_reproduit_en_local(host):
    """La sortie de `make test` lancée en local, avec l'échec, est conservée."""
    trace = host.file("/home/ansible/echec-local.txt")
    assert trace.exists, "Conservez la sortie de make test lancée sur la branche cassée : make test > ~/echec-local.txt 2>&1"
    assert "FAILED" in trace.content_string, "~/echec-local.txt ne montre pas d'échec de test (FAILED)."
