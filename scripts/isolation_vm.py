"""Isolation des labs : dans ce catalogue, c'est le setup qui la porte.

Le catalogue Linux, d'où vient `valider-labs.py`, ramène ses VM à une base
figée entre deux labs (overlay qcow2 sous KVM). Ce catalogue n'en a pas
besoin : chaque `setup.yaml` rejoue le socle commun (forge, runner) puis
SUPPRIME et RECRÉE le dépôt `inventaire` sur la forge, son clone chez
l'apprenant et les environnements de déploiement. L'état noté par les tests
ne dépend donc pas du lab joué juste avant.

Ce module garde l'interface attendue par `valider-labs.py` et ne fait rien.
"""

from __future__ import annotations

from pathlib import Path


class IsolationEteinte(RuntimeError):
    """Interface conservée : jamais levée ici."""


def hotes_du_lab(lab: Path) -> list[str]:
    return []


def snapshot_reset(fqdns: list[str]) -> None:
    return None
