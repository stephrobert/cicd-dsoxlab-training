# certcheck

Signale les certificats TLS d'un parc qui arrivent à expiration. Ce que l'outil
doit faire, vu de l'extérieur, est écrit dans `CONTRAT.md`.

```bash
uv sync                      # installe l'outil et ses outils de développement
bin/certcheck --help         # l'aide
bin/certcheck                # contrôle le parc de inventaire.txt
uv run pytest -v             # les tests
uv run ruff check .          # le linter
uv run ruff format --check . # le formatage
```

L'intégration continue (`.forgejo/workflows/ci.yml`) rejoue ces contrôles à
chaque push sur `main` et à chaque demande de fusion.
