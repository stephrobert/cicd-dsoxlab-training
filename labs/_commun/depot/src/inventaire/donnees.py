"""Lecture et filtrage de l'inventaire, sans aucune dépendance."""

import json


def charger(chemin):
    """Lit le fichier JSON de l'inventaire et renvoie la liste des serveurs."""
    with open(chemin, encoding="utf-8") as fichier:
        donnees = json.load(fichier)
    return donnees["serveurs"]


def filtrer(serveurs, role=None):
    """Garde les serveurs d'un rôle donné, ou tous si aucun rôle n'est demandé."""
    if role is None:
        return list(serveurs)
    return [s for s in serveurs if s.get("role") == role]


def compter_par_role(serveurs):
    """Renvoie un dictionnaire {rôle: nombre de serveurs}."""
    comptes = {}
    for serveur in serveurs:
        role = serveur.get("role", "inconnu")
        comptes[role] = comptes.get(role, 0) + 1
    return comptes
