"""Tests du lab ci-certcheck.

On note l'ÉTAT laissé sur la forge et sur la machine, jamais les commandes :

- main est verte : le défaut de qualité du commit de départ est réparé ;
- une demande de fusion porte un commit rouge dont la CAUSE est un test
  cassé, puis un commit vert ;
- une demande de fusion porte un commit rouge dont la CAUSE est le
  formatage, puis un commit vert ;
- un échec a été rejoué en local, sortie conservée dans ~/echec-local.txt ;
- ~/reponses-ci.yaml décrit les étapes de la pipeline.

La cause d'un commit rouge ne se lit pas dans le statut, qui ne dit que
« failure » : on la RECALCULE en rejouant, sur la VM, les commandes de la
pipeline sur ce commit (pytest d'un côté, ruff format de l'autre).
"""

from __future__ import annotations

import shlex
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_commun"))

from forge import api, statut  # noqa: E402

from conftest import lab_host, message  # noqa: E402

HOTE = "forge-1.lab"
DEPOT = "apprenant/certcheck"
FICHIERS_DE_DEPART = Path(__file__).resolve().parents[2] / "files" / "depot"


@pytest.fixture(scope="module")
def host():
    return lab_host(HOTE)


def _rejouer(host, sha: str, commande: str) -> int:
    """Le code de sortie d'une commande de la pipeline, rejouée sur un commit, dans un clone jetable."""
    script = (
        "set -e; d=$(mktemp -d); trap 'rm -rf \"$d\"' EXIT; "
        "git clone -q http://localhost:3000/apprenant/certcheck.git \"$d/c\" >/dev/null 2>&1; "
        f"cd \"$d/c\"; git checkout -q {shlex.quote(sha)}; "
        "uv sync --locked -q >/dev/null 2>&1; "
        f"rc=0; {{ {commande}; }} >/dev/null 2>&1 || rc=$?; echo $rc"
    )
    res = host.run(f"sudo -u ansible -H bash -c {shlex.quote(script)}")
    try:
        return int(res.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return -1


def commits_de_fusion(host) -> list[tuple[int, str, list[str]]]:
    """Pour chaque demande de fusion (ouverte ou fermée) : son numéro, son dernier commit et les autres.

    Le dernier commit se lit dans `head.sha`, jamais dans l'ordre de la liste
    des commits : Forgejo la rend du plus récent au plus ancien.
    """
    demandes = api(host, f"repos/{DEPOT}/pulls?state=all&limit=50") or []
    rendu = []
    for d in demandes:
        tete = d["head"]["sha"]
        commits = api(host, f"repos/{DEPOT}/pulls/{d['number']}/commits?limit=50") or []
        rendu.append((d["number"], tete, [c["sha"] for c in commits if c["sha"] != tete]))
    return rendu


def _demande_rouge_puis_verte(host, commande_cause: str, commande_saine: str) -> tuple[bool, str]:
    """Une demande dont un commit est rouge PAR `commande_cause` (l'autre contrôle passant), et le dernier vert."""
    constats = []
    for numero, tete, autres in commits_de_fusion(host):
        if statut(host, tete, DEPOT) != "success":
            constats.append(f"#{numero} : dernier commit pas encore vert")
            continue
        for sha in autres:
            if statut(host, sha, DEPOT) != "failure":
                continue
            if _rejouer(host, sha, commande_cause) != 0 and _rejouer(host, sha, commande_saine) == 0:
                return True, ""
        constats.append(f"#{numero} : aucun commit rouge pour cette cause")
    return False, "; ".join(constats) or "aucune demande de fusion"


def test_main_est_verte(host):
    """Le dernier commit de main porte une pipeline réussie : le défaut de départ est réparé."""
    etat = statut(host, "main", DEPOT)
    assert etat == "success", message(
        en=f"Status of main: {etat or 'none'}. Read the log of the red run (Actions tab): "
        "the Quality step names the file and the line. Fix it, commit, push to main, "
        "then wait for the pipeline to finish.",
        fr=f"Statut de main : {etat or 'aucun'}. Lisez le journal du run rouge (onglet Actions) : "
        "l'étape Qualité nomme le fichier et la ligne. Corrigez, commitez, poussez sur main, "
        "puis attendez la fin de la pipeline.",
    )


def test_un_test_casse_puis_repare_dans_une_demande(host):
    """Une demande de fusion porte un commit rouge à cause d'un test, puis un commit vert."""
    ok, pourquoi = _demande_rouge_puis_verte(host, "uv run pytest -q", "uv run ruff check . && uv run ruff format --check .")
    assert ok, message(
        en="No merge request shows a commit turned red by a TEST, followed by a "
        "green commit. On a branch, break a test (or the decision it checks), push, "
        f"open the request, read the red run, fix it and push again. Observed: {pourquoi}.",
        fr="Aucune demande de fusion ne montre un commit rendu rouge par un TEST, suivi d'un "
        "commit vert. Sur une branche, cassez un test (ou la décision qu'il vérifie), poussez, "
        f"ouvrez la demande, lisez le run rouge, corrigez et repoussez. Constat : {pourquoi}.",
    )


def test_un_formatage_casse_puis_repare_dans_une_demande(host):
    """Une demande de fusion porte un commit rouge à cause du formatage, puis un commit vert."""
    ok, pourquoi = _demande_rouge_puis_verte(host, "uv run ruff format --check .", "uv run pytest -q")
    assert ok, message(
        en="No merge request shows a commit turned red by FORMATTING, followed "
        "by a green commit. Write a badly laid out line (extra spaces around an "
        "= sign, for instance), push, read the red run at the Quality step, then "
        f"`uv run ruff format .`, commit and push again. Observed: {pourquoi}.",
        fr="Aucune demande de fusion ne montre un commit rendu rouge par le FORMATAGE, suivi "
        "d'un commit vert. Écrivez une ligne mal mise en page (des espaces en trop autour d'un "
        "signe =, par exemple), poussez, lisez le run rouge à l'étape Qualité, puis "
        f"`uv run ruff format .`, commitez et repoussez. Constat : {pourquoi}.",
    )


def test_echec_reproduit_en_local(host):
    """La sortie locale d'une commande de la pipeline en échec est conservée."""
    trace = host.file("/home/ansible/echec-local.txt")
    assert trace.exists, message(
        en="Keep the output of one of the pipeline's commands replayed locally on a red "
        "commit: uv run pytest > ~/echec-local.txt 2>&1, for instance.",
        fr="Conservez la sortie d'une commande de la pipeline rejouée en local sur un commit "
        "rouge : uv run pytest > ~/echec-local.txt 2>&1, par exemple.",
    )
    contenu = trace.content_string
    assert any(m in contenu for m in ("FAILED", "failed", "would be reformatted", "Would reformat", "Found ")), message(
        en="~/echec-local.txt shows no failure: no failing test (FAILED), no file to "
        "reformat, no linter finding.",
        fr="~/echec-local.txt ne montre pas d'échec : ni test en échec (FAILED), ni fichier à "
        "reformater, ni défaut du linter.",
    )


def test_les_etapes_sont_decrites(host):
    """~/reponses-ci.yaml décrit les étapes de la pipeline fournie."""
    brut = host.file("/home/ansible/reponses-ci.yaml")
    assert brut.exists, message(
        en="~/reponses-ci.yaml has disappeared: run dsoxlab run ci-certcheck again to get it back.",
        fr="~/reponses-ci.yaml a disparu : relancez dsoxlab run ci-certcheck pour le retrouver.",
    )
    try:
        r = yaml.safe_load(brut.content_string) or {}
    except yaml.YAMLError as exc:
        pytest.fail(message(
            en=f"~/reponses-ci.yaml is not valid YAML: {exc}",
            fr=f"~/reponses-ci.yaml n'est pas un YAML valide : {exc}",
        ), pytrace=False)
    doc = yaml.safe_load((FICHIERS_DE_DEPART / ".forgejo" / "workflows" / "ci.yml").read_text(encoding="utf-8"))
    noms = [e["name"] for e in doc["jobs"]["integrer"]["steps"]]
    ordre = [str(x).strip() for x in (r.get("ordre_des_etapes") or [])]
    assert ordre == noms, message(
        en=f"`ordre_des_etapes` is {ordre}: copy the name: of each step of "
        ".forgejo/workflows/ci.yml, in the file's order.",
        fr=f"`ordre_des_etapes` vaut {ordre} : recopiez le name: de chaque étape de "
        ".forgejo/workflows/ci.yml, dans l'ordre du fichier.",
    )
    installe = next(e["name"] for e in doc["jobs"]["integrer"]["steps"] if "uv sync" in str(e.get("run", "")))
    assert str(r.get("etape_des_dependances") or "").strip() == installe, message(
        en="`etape_des_dependances`: the step installing the dependencies is the one running "
        "uv sync, according to the lock file uv.lock.",
        fr="`etape_des_dependances` : l'étape qui installe les dépendances est celle qui lance "
        "uv sync, d'après le fichier verrouillé uv.lock.",
    )
    qualite = next(e["name"] for e in doc["jobs"]["integrer"]["steps"] if "ruff check" in str(e.get("run", "")))
    assert str(r.get("etape_en_echec_sur_main") or "").strip() == qualite, message(
        en="`etape_en_echec_sur_main`: open main's first run in the Actions tab; "
        "the step marked as failed is the first one that returned a non-zero code.",
        fr="`etape_en_echec_sur_main` : ouvrez le premier run de main dans l'onglet Actions ; "
        "l'étape marquée en échec est la première qui a rendu un code non nul.",
    )
