"""Tests de l'épreuve level-exams-chaine.

On note l'ÉTAT final, sans indice : la chaîne est honnête (aucun test ignoré,
aucune étape hors make, action épinglée par SHA, aucun secret affiché,
publication réservée aux étiquettes), verte, une version corrigée est publiée
puis promue en production par son empreinte, sans reconstruction, et le
fichier risques.md nomme les défauts de sécurité trouvés.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "_commun"))

from forge import (
    api,
    declencheurs,
    etapes_run,
    fichier,
    statut,
    workflows,
)

from conftest import lab_host, message

HOTE = "forge-1.lab"
JOURNAL = "/var/log/inventaire/deploiements.log"
SHA = re.compile(r"@[0-9a-f]{40}(\s|$)")


@pytest.fixture(scope="module")
def host():
    return lab_host(HOTE)


@pytest.fixture
def pipelines(host):
    return workflows(host, "main")


def _versions_publiees(host):
    paquets = api(host, "packages/apprenant?type=generic&q=inventaire") or []
    versions = [p["version"] for p in paquets if p.get("name") == "inventaire"]
    return sorted(versions, key=lambda v: tuple(int(x) if x.isdigit() else 0 for x in v.split(".")))


def _sha_publie(host, version):
    fichiers = api(host, f"packages/apprenant/generic/inventaire/{version}/files") or []
    return next((f["sha256"] for f in fichiers if f["name"] == f"inventaire-{version}.pyz"), None)


def _nouvelle_version(host):
    autres = [v for v in _versions_publiees(host) if v != "1.0.0"]
    return autres[-1] if autres else None


def test_aucun_test_ignore_ni_etape_hors_make(pipelines):
    """La pipeline d'intégration lance lint, test et build par make, dans l'ordre, sans masquer un échec."""
    assert pipelines, message(
        en="No pipeline on main.",
        fr="Aucune pipeline sur main.",
    )
    integration = [d for d in pipelines.values() if "push" in declencheurs(d) or "pull_request" in declencheurs(d)]
    assert integration, message(
        en="No integration pipeline (push, pull_request).",
        fr="Aucune pipeline d'intégration (push, pull_request).",
    )
    for doc in integration:
        assert "MAKEFLAGS" not in str(doc.get("env", "")), message(
            en="MAKEFLAGS at the workflow level can make failures be ignored.",
            fr="MAKEFLAGS au niveau du workflow peut faire ignorer les échecs.",
        )
        assert "defaults" not in doc, message(
            en="The workflow's defaults settings change the way the steps run.",
            fr="Les réglages defaults du workflow changent la façon dont les étapes s'exécutent.",
        )
        for job in (doc.get("jobs") or {}).values():
            assert "continue-on-error" not in job, message(
                en="A job ignores its failures (continue-on-error).",
                fr="Un job ignore ses échecs (continue-on-error).",
            )
            assert "MAKEFLAGS" not in str(job.get("env", "")) and "defaults" not in job, message(
                en="The job changes the way make or the shell runs.",
                fr="Le job modifie l'exécution de make ou du shell.",
            )
            assert not any("shell" in e or "MAKEFLAGS" in str(e.get("env", "")) for e in job.get("steps") or []), message(
                en="A step changes shell or MAKEFLAGS.",
                fr="Une étape change de shell ou de MAKEFLAGS.",
            )
            etapes = [e for e in job.get("steps") or [] if "run" in e]
            ordre = [str(e["run"]).strip() for e in etapes]
            for cible in ("make lint", "make test", "make build"):
                assert cible in ordre, message(
                    en=f"The pipeline does not call {cible} as a step of its own.",
                    fr=f"La pipeline n'appelle pas {cible} comme étape à part entière.",
                )
            assert ordre.index("make lint") < ordre.index("make test") < ordre.index("make build"), message(
                en="Expected order: lint, test, build.",
                fr="Ordre attendu : lint, test, build.",
            )
            for e in etapes:
                if str(e["run"]).strip() in ("make lint", "make test", "make build"):
                    assert "if" not in e and "continue-on-error" not in e, message(
                        en=f"The step {e['run']} is conditional or tolerates failure.",
                        fr=f"L'étape {e['run']} est conditionnelle ou tolère l'échec.",
                    )
    commandes = [c for doc in pipelines.values() for c in etapes_run(doc)]
    for c in commandes:
        assert "|| true" not in c and "||true" not in c, message(
            en=f"A failure is still masked: {c}",
            fr=f"Un échec est encore masqué : {c}",
        )
        for ligne in (brute.strip() for brute in c.splitlines() if brute.strip()):
            assert ligne.startswith("make"), message(
                en=f"Step outside the Makefile, impossible to replay as is locally: {ligne}",
                fr=f"Étape hors du Makefile, impossible à rejouer telle quelle en local : {ligne}",
            )


def test_actions_epinglees_par_sha(pipelines):
    """Chaque action est épinglée par le SHA de son commit."""
    for nom, doc in pipelines.items():
        for job in (doc.get("jobs") or {}).values():
            for etape in job.get("steps") or []:
                if "uses" in etape:
                    assert SHA.search(str(etape["uses"]) + " "), message(
                        en=f"{nom}: action not pinned by SHA: {etape['uses']}",
                        fr=f"{nom} : action non épinglée par SHA : {etape['uses']}",
                    )


def test_aucun_secret_affiche(pipelines):
    """Aucune étape ne manipule le jeton dans sa commande : il ne sert que par l'environnement de make publish."""
    for nom, doc in pipelines.items():
        assert "secrets." not in str(doc.get("env", "")), message(
            en=f"{nom}: a secret is exposed to the whole workflow.",
            fr=f"{nom} : un secret est exposé à tout le workflow.",
        )
        for job in (doc.get("jobs") or {}).values():
            assert "secrets." not in str(job.get("env", "")), message(
                en=f"{nom}: a secret is exposed to a whole job.",
                fr=f"{nom} : un secret est exposé à tout un job.",
            )
            for etape in job.get("steps") or []:
                env = str(etape.get("env", ""))
                run = str(etape.get("run", ""))
                assert "REGISTRE_JETON" not in run, message(
                    en=f"{nom}: the token appears in a command: {run}",
                    fr=f"{nom} : le jeton apparaît dans une commande : {run}",
                )
                if "secrets." in env:
                    assert run.strip().startswith("make publish"), message(
                        en=f"{nom}: a secret is passed to a step other than make publish: {run}",
                        fr=f"{nom} : un secret est passé à une étape autre que make publish : {run}",
                    )


def test_publication_reservee_aux_etiquettes(pipelines):
    """Seule une étiquette v* publie : ni une branche, ni une demande de fusion."""
    for nom, doc in pipelines.items():
        for job in (doc.get("jobs") or {}).values():
            for etape in job.get("steps") or []:
                if "make publish" in str(etape.get("run", "")):
                    condition = str(etape.get("if", "")) + str(job.get("if", ""))
                    on = declencheurs(doc)
                    seulement_tags = set(on) == {"push"} and set(on.get("push") or {}) == {"tags"}
                    assert ("refs/tags/v" in condition and "!" not in condition) or seulement_tags, message(
                        en=f"{nom}: make publish runs on every branch; reserve it for v* tags.",
                        fr=f"{nom} : make publish tourne sur toute branche ; réservez-le aux étiquettes v*.",
                    )


def test_chaine_verte_et_honnete(host, pipelines):
    """main est vert sans rien masquer : tests d'origine intacts, recette make test inchangée."""
    commandes = [c for doc in pipelines.values() for c in etapes_run(doc)]
    assert not any("|| true" in c or "||true" in c for c in commandes), message(
        en="A green obtained by masking a failure does not count.",
        fr="Un vert obtenu en masquant un échec ne compte pas.",
    )
    origine = host.check_output("cat /root/tests-origine.sha256").strip()
    actuel = host.check_output(
        "J=$(cat /etc/forgejo/jeton-apprenant); curl -fsS -H \"Authorization: token $J\" "
        "'http://localhost:3000/api/v1/repos/apprenant/inventaire/raw/tests/test_donnees.py?ref=main' | sha256sum | cut -d' ' -f1"
    ).strip()
    assert actuel == origine, message(
        en="tests/test_donnees.py was modified: it was the code that had to be fixed, not the test.",
        fr="tests/test_donnees.py a été modifié : c'est le code qu'il fallait corriger, pas le test.",
    )
    makefile = fichier(host, "Makefile") or ""
    assert len(re.findall(r"^test\s*:", makefile, re.M)) == 1, message(
        en="The Makefile defines several test rules.",
        fr="Le Makefile définit plusieurs règles test.",
    )
    assert re.search(r"^test:\n\tpython3 -m unittest discover -s tests -v$", makefile, re.M), message(
        en="The recipe of make test was modified (a - prefix, || true, another command).",
        fr="La recette de make test a été modifiée (préfixe -, || true, autre commande).",
    )
    assert statut(host, "main") == "success", message(
        en=f"Status of main: {statut(host, 'main')}",
        fr=f"Statut de main : {statut(host, 'main')}",
    )


def test_production_compte_juste(host):
    """La production sert un inventaire correctement compté (le défaut du code est corrigé)."""
    rendu = json.loads(host.check_output("curl -fsS http://127.0.0.1:8082/serveurs"))
    assert rendu.get("par_role") == {"web": 2, "base": 1}, message(
        en=f"Production counts wrongly: {rendu.get('par_role')}",
        fr=f"La production compte mal : {rendu.get('par_role')}",
    )


def test_jeton_qui_a_fui_revoque(host):
    """Le jeton lisible dans le journal n'existe plus : il a été révoqué, et un nouveau publie."""
    nom = host.check_output("cat /root/jeton-fuite-nom").strip()
    jetons = json.loads(host.check_output(
        "curl -fsS -u apprenant:apprenant-lab http://localhost:3000/api/v1/users/apprenant/tokens"
    ))
    assert nom not in [j.get("name") for j in jetons], message(
        en="The token leaked in the log is still valid: revoke it and replace the REGISTRE_JETON secret.",
        fr="Le jeton qui a fui dans le journal est toujours valide : révoquez-le et remplacez le secret REGISTRE_JETON.",
    )


def test_version_corrigee_publiee(host):
    """Une version corrigée, autre que 1.0.0, est publiée depuis une étiquette verte."""
    version = _nouvelle_version(host)
    assert version, message(
        en="No version other than 1.0.0 in the registry: 1.0.0 is immutable, publish a new version.",
        fr="Aucune version autre que 1.0.0 dans le registre : 1.0.0 est immuable, publiez une nouvelle version.",
    )
    assert statut(host, f"v{version}") == "success", message(
        en=f"The pipeline of tag v{version} is not green.",
        fr=f"La pipeline de l'étiquette v{version} n'est pas verte.",
    )


def test_deploiement_sans_reconstruction(host, pipelines):
    """Le déploiement installe un artefact publié : ni build, ni entrée interpolée dans run:."""
    deploiement = [d for d in pipelines.values() if "workflow_dispatch" in declencheurs(d)]
    assert deploiement, message(
        en="No on-demand deployment pipeline on main.",
        fr="Aucune pipeline de déploiement à la demande sur main.",
    )
    for doc in deploiement:
        commandes = etapes_run(doc)
        assert any("make deployer" in c for c in commandes), message(
            en="The deployment must go through make deployer.",
            fr="Le déploiement doit passer par make deployer.",
        )
        for c in commandes:
            assert "make build" not in c and "zipapp" not in c, message(
                en=f"The deployment rebuilds the artefact: {c}",
                fr=f"Le déploiement reconstruit l'artefact : {c}",
            )
            assert "${{" not in c, message(
                en=f"An input is interpolated into run:: {c}",
                fr=f"Une entrée est interpolée dans run: : {c}",
            )
            if "make deployer" in c:
                assert "=" not in c, message(
                    en=f"Values passed on make's command line, which would expand them: {c}",
                    fr=f"Valeurs passées sur la ligne de commande de make, qui les développerait : {c}",
                )
    runs = (api(host, "repos/apprenant/inventaire/actions/tasks") or {}).get("workflow_runs", [])
    assert any(r.get("event") == "workflow_dispatch" and r.get("status") == "success" for r in runs), message(
        en="No successful on-demand deployment in the forge.",
        fr="Aucun déploiement à la demande réussi dans la forge.",
    )


def test_promotion_par_empreinte(host):
    """La version corrigée tourne en recette et en production, même empreinte, imposée en production."""
    version = _nouvelle_version(host)
    assert version, message(
        en="No fixed version published.",
        fr="Aucune version corrigée publiée.",
    )
    attendu = _sha_publie(host, version)
    journal = host.file(JOURNAL).content_string if host.file(JOURNAL).exists else ""
    lignes = [ligne.split() for ligne in journal.splitlines()
              if len(ligne.split()) >= 4]
    recette = [entree for entree in lignes
               if entree[1] == "recette" and entree[2] == version
               and entree[3] == attendu]
    prod = [entree for entree in lignes
            if entree[1] == "production" and entree[2] == version
            and entree[3] == attendu and entree[4:] == ["empreinte-imposee"]]
    assert recette, message(
        en=f"{version} was not deployed to staging with the registry's checksum.",
        fr=f"{version} n'a pas été déployée en recette avec l'empreinte du registre.",
    )
    assert prod, message(
        en=f"{version} was not promoted to production enforcing the staging checksum.",
        fr=f"{version} n'a pas été promue en production en imposant l'empreinte de la recette.",
    )
    for env, port in (("recette", 8081), ("production", 8082)):
        f = host.file(f"/opt/inventaire/{env}/inventaire.pyz")
        assert f.exists and f.sha256sum == attendu, message(
            en=f"The artefact of {env} is not the registry's.",
            fr=f"L'artefact de {env} n'est pas celui du registre.",
        )
        rendu = json.loads(host.check_output(f"curl -fsS http://127.0.0.1:{port}/version"))
        assert rendu == {"version": version, "environnement": env}, message(
            en=f"{env} answers {rendu}.",
            fr=f"{env} répond {rendu}.",
        )


def test_risques_listes(host):
    """risques.md nomme les cinq défauts de sécurité semés."""
    texte = (fichier(host, "risques.md") or "").lower()
    assert texte, message(
        en="Write risques.md at the repository's root, on main.",
        fr="Écrivez risques.md à la racine du dépôt, sur main.",
    )
    attendus = {
        "le secret affiché dans le journal": ("secret", "jeton"),
        "l'action épinglée par une étiquette": ("épingl",),
        "la publication ouverte à toute branche": ("branche",),
        "l'artefact reconstruit au déploiement": ("reconstru",),
        "l'entrée interpolée dans la commande de déploiement": ("injection", "interpol"),
    }
    manquants = [k for k, mots in attendus.items() if not any(m in texte for m in mots)]
    assert not manquants, message(
        en=f"risques.md does not mention: {', '.join(manquants)}.",
        fr=f"risques.md ne parle pas de : {', '.join(manquants)}.",
    )
