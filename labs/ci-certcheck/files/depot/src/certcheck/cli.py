"""L'interface de certcheck : arguments, configuration, sorties et codes de sortie.

`main` est la fonction que lance la commande `certcheck` (voir
[project.scripts] dans pyproject.toml) : l'entier qu'elle rend devient le
code de sortie du processus.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
from pathlib import Path

from certcheck import __version__
from certcheck.certificats import ErreurUsage, analyser, aujourd_hui, lire_inventaire

SEUIL_PAR_DEFAUT = 30


def code_de_sortie(resultats: list[dict]) -> int:
    statuts = {r["status"] for r in resultats}
    if "error" in statuts:
        return 2
    if statuts & {"warning", "expired"}:
        return 1
    return 0


def en_texte(resultats: list[dict]) -> str:
    """Une ligne par hôte : l'hôte, son statut et les jours restants, séparés par des tabulations."""
    return "\n".join(f"{r['host']}\t{r['status']}\t{r['days_left']}" for r in resultats)


def en_json(resultats: list[dict], seuil: int) -> str:
    return json.dumps({"threshold_days": seuil, "certificates": resultats}, ensure_ascii=False, indent=2)


def seuil_depuis(argument: int | None) -> int:
    if argument is not None:
        return argument
    valeur = os.environ.get("CERTCHECK_DAYS")
    if valeur is None:
        return SEUIL_PAR_DEFAUT
    if not valeur.isdigit():
        raise ErreurUsage(f"CERTCHECK_DAYS invalide : {valeur!r} (entier positif attendu)")
    return int(valeur)


def jours_positifs(valeur: str) -> int:
    """Le type de --days : argparse transforme l'exception en message et en code 2."""
    if not valeur.isdigit():
        raise argparse.ArgumentTypeError(f"nombre de jours positif attendu : {valeur!r}")
    return int(valeur)


def analyseur() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="certcheck",
        description="Signale les certificats TLS d'un parc qui arrivent à expiration.",
        epilog="Codes de sortie : 0 tout est valide, 1 certificat à renouveler, 2 usage ou entrée inexploitable.",
    )
    p.add_argument(
        "--inventory", type=Path, default=Path("inventaire.txt"), help="inventaire des hôtes (défaut : inventaire.txt)"
    )
    p.add_argument(
        "--days",
        type=jours_positifs,
        metavar="N",
        help=f"seuil d'alerte en jours (défaut : $CERTCHECK_DAYS, sinon {SEUIL_PAR_DEFAUT})",
    )
    p.add_argument("--format", choices=("text", "json"), default="text", help="format de la sortie standard")
    p.add_argument("--version", action="version", version=f"certcheck {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = analyseur().parse_args(argv)  # usage incorrect : argparse écrit sur stderr et sort en 2
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s", stream=sys.stderr)
    try:
        seuil = seuil_depuis(args.days)
        resultats = analyser(lire_inventaire(args.inventory), seuil, aujourd_hui())
    except ErreurUsage as exc:
        print(f"certcheck: {exc}", file=sys.stderr)
        return 2
    print(en_json(resultats, seuil) if args.format == "json" else en_texte(resultats))
    return code_de_sortie(resultats)
