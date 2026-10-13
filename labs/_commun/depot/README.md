# inventaire

Un petit service HTTP qui sert la liste des serveurs d'une équipe, écrit en
Python sans aucune dépendance.

```bash
make lint     # analyse statique (pyflakes)
make test     # tests unitaires (unittest)
make build    # construit dist/inventaire-<version>.pyz et son empreinte
```

Le service lit sa configuration dans l'environnement : `INVENTAIRE_ENV`,
`INVENTAIRE_PORT`, `INVENTAIRE_DONNEES`.
