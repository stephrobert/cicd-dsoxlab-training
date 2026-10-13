"""Lecture de l'état de la forge du lab, pour les tests des labs.

Les tests lisent la forge par son API, DEPUIS la VM (curl en root, jeton de
l'apprenant posé par le socle) : rien n'est exposé hors de la machine. Ils
notent l'état laissé (fichiers du dépôt, statuts de commit, demandes de
fusion), jamais les commandes tapées.
"""

from __future__ import annotations

import json
import shlex

import yaml

FORGE = "http://localhost:3000"
DEPOT = "apprenant/inventaire"


def api(host, chemin: str):
    """GET sur l'API de la forge ; rend le JSON, ou None si la ressource manque."""
    cmd = (
        'J=$(cat /etc/forgejo/jeton-apprenant); '
        f'curl -s -w "\\n%{{http_code}}" -H "Authorization: token $J" '
        f'{shlex.quote(FORGE + "/api/v1/" + chemin)}'
    )
    sortie = host.check_output(cmd)
    corps, _, code = sortie.rpartition("\n")
    if code.strip() != "200":
        return None
    return json.loads(corps)


def fichier(host, chemin: str, ref: str = "main") -> str | None:
    """Contenu d'un fichier du dépôt sur une référence, ou None."""
    cmd = (
        'J=$(cat /etc/forgejo/jeton-apprenant); '
        f'curl -s -f -H "Authorization: token $J" '
        f'{shlex.quote(f"{FORGE}/api/v1/repos/{DEPOT}/raw/{chemin}?ref={ref}")}'
    )
    res = host.run(cmd)
    return res.stdout if res.rc == 0 else None


def workflows(host, ref: str = "main") -> dict[str, dict]:
    """Les fichiers de pipeline du dépôt, parsés : {nom: document YAML}."""
    liste = api(host, f"repos/{DEPOT}/contents/.forgejo/workflows?ref={ref}") or []
    rendus = {}
    for entree in liste:
        if entree.get("type") != "file" or not entree["name"].endswith((".yml", ".yaml")):
            continue
        texte = fichier(host, f".forgejo/workflows/{entree['name']}", ref)
        if texte is None:
            continue
        try:
            rendus[entree["name"]] = yaml.safe_load(texte) or {}
        except yaml.YAMLError:
            rendus[entree["name"]] = {"__invalide__": True}
    return rendus


def declencheurs(doc: dict) -> dict:
    """Le bloc `on:` d'un workflow. PyYAML lit la clé `on` comme le booléen True."""
    bloc = doc.get("on", doc.get(True, {}))
    if isinstance(bloc, str):
        return {bloc: None}
    if isinstance(bloc, list):
        return {cle: None for cle in bloc}
    return bloc or {}


def etapes_run(doc: dict) -> list[str]:
    """Toutes les commandes `run:` de tous les jobs d'un workflow."""
    commandes = []
    for job in (doc.get("jobs") or {}).values():
        for etape in job.get("steps") or []:
            if "run" in etape:
                commandes.append(str(etape["run"]).strip())
    return commandes


def statut(host, ref: str) -> str | None:
    """État combiné des statuts de commit d'une référence (success, failure, pending)."""
    rendu = api(host, f"repos/{DEPOT}/commits/{ref}/status")
    if not rendu or not rendu.get("statuses"):
        return None
    return rendu.get("state")
