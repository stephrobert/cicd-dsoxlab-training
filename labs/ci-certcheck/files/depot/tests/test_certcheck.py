"""Les tests de certcheck : `uv run pytest -v`."""

from datetime import date
from pathlib import Path

from certcheck import certificats

RACINE = Path(__file__).resolve().parent.parent
CERTS = RACINE / "certs"
AUJOURD_HUI = date(2026, 6, 1)  # la date est passée en argument : le verdict ne dépend pas du jour


def test_un_certificat_lointain_est_ok():
    resultats = certificats.analyser([("web-01", CERTS / "web-01.pem")], 30, AUJOURD_HUI)
    assert resultats[0]["status"] == "ok"
    assert resultats[0]["not_after"] == "2045-06-15"


def test_un_certificat_expire_est_signale():
    resultats = certificats.analyser([("web-02", CERTS / "web-02.pem")], 30, AUJOURD_HUI)
    assert resultats[0]["status"] == "expired"


def test_le_seuil_est_inclusif():
    assert certificats.statut(30, 30) == "warning"
    assert certificats.statut(31, 30) == "ok"


def test_un_jour_a_un_chiffre_est_lu():
    assert certificats.date_expiration(CERTS / "vpn-01.pem") == date(2031, 3, 5)


def test_un_certificat_absent_est_en_erreur(tmp_path):
    resultats = certificats.analyser([("absent", tmp_path / "absent.pem")], 30, AUJOURD_HUI)
    assert resultats[0]["status"] == "error"
