"""Point d'entrée HTTP du service inventaire.

La configuration vient de l'ENVIRONNEMENT, jamais de l'artefact : le même
fichier .pyz tourne en recette et en production, seules ces variables changent.

  INVENTAIRE_ENV      nom de l'environnement (recette, production)
  INVENTAIRE_PORT     port d'écoute
  INVENTAIRE_DONNEES  chemin du fichier JSON de l'inventaire
"""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from inventaire import __version__
from inventaire.donnees import charger, compter_par_role, filtrer


class Gestionnaire(BaseHTTPRequestHandler):
    def _repondre(self, code, corps):
        contenu = json.dumps(corps, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(contenu)))
        self.end_headers()
        self.wfile.write(contenu)

    def do_GET(self):
        environnement = os.environ.get("INVENTAIRE_ENV", "local")
        if self.path == "/version":
            self._repondre(200, {"version": __version__, "environnement": environnement})
            return
        if self.path.startswith("/serveurs"):
            serveurs = charger(os.environ.get("INVENTAIRE_DONNEES", "serveurs.json"))
            role = None
            if "?role=" in self.path:
                role = self.path.split("?role=", 1)[1]
            self._repondre(200, {"serveurs": filtrer(serveurs, role), "par_role": compter_par_role(serveurs)})
            return
        self._repondre(404, {"erreur": "chemin inconnu"})

    def log_message(self, format, *args):
        pass


def main():
    port = int(os.environ.get("INVENTAIRE_PORT", "8080"))
    HTTPServer(("127.0.0.1", port), Gestionnaire).serve_forever()


if __name__ == "__main__":
    main()
