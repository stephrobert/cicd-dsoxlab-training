"""L'inventaire et ses certificats : lecture, date d'expiration, statut."""

from __future__ import annotations

import logging
import os
import subprocess
from datetime import UTC, date, datetime
from pathlib import Path

log = logging.getLogger("certcheck")


class ErreurUsage(Exception):
    """Entrée ou configuration inexploitable : l'interface la traduit en code 2."""


def lire_inventaire(chemin: Path) -> list[tuple[str, Path]]:
    """Les couples (hôte, certificat) de l'inventaire, dans l'ordre du fichier."""
    try:
        texte = chemin.read_text(encoding="utf-8")
    except OSError as exc:
        raise ErreurUsage(f"inventaire illisible : {chemin} ({exc.strerror})") from exc
    entrees = []
    for numero, ligne in enumerate(texte.splitlines(), 1):
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#"):
            continue
        champs = ligne.split()
        if len(champs) != 2:
            raise ErreurUsage(f"{chemin}, ligne {numero} : « <hôte> <certificat> » attendu")
        hote, certificat = champs
        entrees.append((hote, chemin.parent / certificat))
    return entrees


def date_expiration(certificat: Path) -> date:
    """La date notAfter du certificat, lue par openssl. ValueError s'il est absent ou illisible."""
    res = subprocess.run(
        ["openssl", "x509", "-enddate", "-noout", "-in", str(certificat)],
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode != 0:
        raise ValueError(f"certificat illisible : {certificat}")
    brut = res.stdout.strip().partition("=")[2]  # « Mar  5 12:00:00 2031 GMT »
    return datetime.strptime(brut, "%b %d %H:%M:%S %Y %Z").date()


def aujourd_hui() -> date:
    """La date du jour, ou celle de CERTCHECK_NOW (AAAA-MM-JJ) : l'horloge s'injecte pour être testée."""
    valeur = os.environ.get("CERTCHECK_NOW")
    if not valeur:
        return datetime.now(UTC).date()
    try:
        return date.fromisoformat(valeur)
    except ValueError as exc:
        raise ErreurUsage(f"CERTCHECK_NOW invalide : {valeur!r} (AAAA-MM-JJ attendu)") from exc


def statut(jours: int, seuil: int) -> str:
    if jours < 0:
        return "expired"
    if jours <= seuil:
        return "warning"
    return "ok"


def analyser(entrees: list[tuple[str, Path]], seuil: int, jour: date) -> list[dict]:
    resultats = []
    for hote, certificat in entrees:
        try:
            fin = date_expiration(certificat)
        except ValueError as exc:
            log.error("%s : %s", hote, exc)
            resultats.append({"host": hote, "not_after": None, "days_left": None, "status": "error"})
            continue
        jours = (fin - jour).days
        resultats.append(
            {"host": hote, "not_after": fin.isoformat(), "days_left": jours, "status": statut(jours, seuil)}
        )
    return resultats
