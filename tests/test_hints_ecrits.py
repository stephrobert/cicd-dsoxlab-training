"""Méta-tests du dépôt : les indices doivent avoir été écrits.

Le générateur de labs pose des indices provisoires, du genre « Nudge à écrire :
orienter vers le bon concept sans donner la méthode ». Ils sont encodés en
base64, comme les vrais, pour qu'un apprenant n'y accède pas en ouvrant le
fichier. C'est justement ce qui les a rendus invisibles : `grep` ne les trouve
pas, une relecture de PR non plus, et deux labs ont été livrés validés avec des
indices que personne n'avait écrits.

On les décode donc, et on refuse le gabarit.

La liste `DETTE` porte les labs qui n'ont pas encore été repris. Elle n'est PAS
une exemption commode : le test refuse aussi qu'un lab y reste alors que ses
indices ont été écrits. Sans cette seconde moitié, la liste ne décroîtrait
jamais et plus personne ne la regarderait.
"""

import base64
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
LABS = REPO / "labs"

# Formules que le générateur laisse derrière lui, dans les deux langues.
#
# Ce sont les PHRASES du gabarit, pas des fragments. La première version
# cherchait « à écrire » et « to write », et cela a coûté un faux positif
# mesuré le 2026-09-25 : l'indice anglais de `environments/when-to-use-workspaces`
# dit « the block **to write** is a data "terraform_remote_state" », une tournure
# parfaitement légitime dans un indice rédigé. Le lab était retenu dans la dette
# alors que ses trois indices étaient écrits, et rien ne pouvait l'en sortir.
#
# Un détecteur trop large ne se contente pas de crier à tort : il rend la liste
# de dette fausse, donc inutilisable.
MARQUEURS = (
    "Nudge à écrire",
    "Méthode à écrire",
    "Quasi-solution à écrire",
    "Nudge to write",
    "Method to write",
    "Near-solution to write",
    "A_COMPLETER",
)

# Convention de ce dépôt, mesurée sur ses cinq labs le 2026-10-17 : trois OU
# quatre indices, aux coûts strictement croissants par paliers de cinq à partir
# de dix. Le catalogue Cloud en impose exactement trois, à 10, 15 et 20 ; c'est
# sa convention, pas celle d'ici, et deux labs de ce dépôt portent un quatrième
# indice qui mérite d'exister.
#
# Ce qui compte n'est pas le nombre, c'est que le coût CROISSE avec
# l'explicitation : un indice qui donne presque la solution ne peut pas coûter
# moins cher que celui qui oriente. Les deux labs concernés affichaient
# [10, 15, 20, 15] et [10, 10, 15, 20], donc un palier qui redescend et un
# palier doublé : l'apprenant payait le plus explicite au prix du plus vague.
PREMIER_COUT = 10
PAS = 5


def couts_attendus(nombre: int) -> list[int]:
    return [PREMIER_COUT + PAS * i for i in range(nombre)]

# Labs dont les indices sont encore ceux du générateur, mesurés le 2026-09-18.
# Un lab repris se retire d'ici, et le test le vérifie.
DETTE: set[str] = set()


def labs_avec_indices() -> list[str]:
    return sorted(
        str(f.parent.parent.relative_to(LABS))
        for f in LABS.rglob("challenge/hints.yaml")
    )


def type_de_lab(rel: str) -> str:
    """`lab_type` du lab, qui vaut `lab` par défaut dans le contrat dsoxlab."""
    contenu = yaml.safe_load((LABS / rel / "lab.yaml").read_text(encoding="utf-8")) or {}
    return str(contenu.get("lab_type") or "lab")


def indices_en_clair(rel: str) -> list[dict]:
    """Les indices d'un lab, décodés. La liste peut être vide."""
    fichier = LABS / rel / "challenge" / "hints.yaml"
    contenu = yaml.safe_load(fichier.read_text(encoding="utf-8")) or {}
    clairs = []
    for h in contenu.get("hints") or []:
        clairs.append(
            {
                "cost": h.get("cost"),
                "fr": base64.b64decode(h.get("text_fr", "")).decode("utf-8", "replace"),
                "en": base64.b64decode(h.get("text_en", "")).decode("utf-8", "replace"),
            }
        )
    return clairs


def porte_le_gabarit(clairs: list[dict]) -> bool:
    return any(m in i[langue] for i in clairs for langue in ("fr", "en") for m in MARQUEURS)


@pytest.mark.parametrize("rel", labs_avec_indices())
def test_les_indices_ne_sont_pas_ceux_du_generateur(rel: str) -> None:
    clairs = indices_en_clair(rel)
    if not clairs:
        # Une ÉPREUVE ne donne pas d'indices : c'est ce qu'elle mesure. Exiger
        # des indices de `lab_type: challenge` enseignerait le contraire de ce
        # que l'épreuve est. Un lab ordinaire, lui, doit les porter.
        assert type_de_lab(rel) == "challenge", (
            f"{rel} : hints.yaml ne porte aucun indice, et ce lab n'est pas "
            "une épreuve."
        )
        return

    if porte_le_gabarit(clairs):
        assert rel in DETTE, (
            f"{rel} : les indices sont encore ceux du générateur.\n"
            f"Premier indice décodé : {clairs[0]['fr']!r}\n\n"
            "Quatre indices bilingues de coût croissant, du plus vague au plus "
            "explicite, sans jamais donner le bloc complet. Ils sont en base64 "
            "pour qu'un apprenant n'y accède pas en ouvrant le fichier."
        )
        return

    assert rel not in DETTE, (
        f"{rel} : les indices ont été écrits, mais le lab figure encore dans "
        "DETTE. Retirez-le de la liste, sinon elle ne décroît jamais et plus "
        "personne ne la regarde."
    )


@pytest.mark.parametrize("rel", sorted(set(labs_avec_indices()) - DETTE))
def test_indices_de_cout_croissant(rel: str) -> None:
    """Un lab repris porte trois ou quatre indices, aux coûts croissants."""
    couts = [i["cost"] for i in indices_en_clair(rel)]
    if not couts and type_de_lab(rel) == "challenge":
        pytest.skip(f"{rel} est une épreuve : elle ne donne pas d'indices.")
    assert 3 <= len(couts) <= 4, (
        f"{rel} : {len(couts)} indice(s). Trois paliers, quatre quand le lab "
        "le justifie, du plus vague au plus explicite."
    )
    assert couts == couts_attendus(len(couts)), (
        f"{rel} : les coûts des indices valent {couts}, attendu "
        f"{couts_attendus(len(couts))}. Le coût croît avec l'explicitation : "
        "le dernier indice en dit le plus, il coûte donc le plus cher."
    )


@pytest.mark.parametrize("rel", sorted(set(labs_avec_indices()) - DETTE))
def test_les_deux_langues_sont_renseignees(rel: str) -> None:
    """`text_fr` recopié de l'anglais signale une traduction jamais faite.

    L'égalité n'est pas fautive indice par indice : le dernier palier est
    parfois un extrait de HCL, identique dans les deux langues par nature. Ce
    qui est fautif, c'est que le lab ENTIER soit identique en français et en
    anglais, car alors personne n'a traduit.
    """
    clairs = indices_en_clair(rel)
    if not clairs and type_de_lab(rel) == "challenge":
        pytest.skip(f"{rel} est une épreuve : elle ne donne pas d'indices.")
    for rang, indice in enumerate(clairs, start=1):
        assert indice["fr"].strip(), f"{rel} : indice {rang} sans texte français."
        assert indice["en"].strip(), f"{rel} : indice {rang} sans texte anglais."

    # `any()` sur une liste vide vaut False : sans ce garde-fou, un lab sans
    # indice serait accusé de n'avoir jamais été traduit.
    assert clairs and any(i["fr"] != i["en"] for i in clairs), (
        f"{rel} : les trois indices portent le même texte en français et en "
        "anglais. `text_fr` est une copie de l'anglais tant que personne n'est "
        "passé."
    )


def test_la_dette_ne_designe_que_des_labs_existants() -> None:
    """Un lab renommé ou supprimé ne doit pas laisser une entrée fantôme."""
    fantomes = DETTE - set(labs_avec_indices())
    assert not fantomes, (
        f"DETTE désigne des labs qui n'existent pas : {sorted(fantomes)}."
    )
