import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from inventaire.donnees import charger, compter_par_role, filtrer  # noqa: E402

SERVEURS = [
    {"nom": "web-1", "role": "web"},
    {"nom": "web-2", "role": "web"},
    {"nom": "db-1", "role": "base"},
]


class TestFiltrer(unittest.TestCase):
    def test_sans_role_rend_tout(self):
        self.assertEqual(len(filtrer(SERVEURS)), 3)

    def test_par_role(self):
        self.assertEqual([s["nom"] for s in filtrer(SERVEURS, "web")], ["web-1", "web-2"])

    def test_role_absent(self):
        self.assertEqual(filtrer(SERVEURS, "cache"), [])


class TestCompter(unittest.TestCase):
    def test_compte_par_role(self):
        self.assertEqual(compter_par_role(SERVEURS), {"web": 2, "base": 1})


class TestCharger(unittest.TestCase):
    def test_lit_le_fichier(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"serveurs": SERVEURS}, f)
        try:
            self.assertEqual(len(charger(f.name)), 3)
        finally:
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
