# Challenge: artefacts

## Mission

On `forge-1.lab`, in `~/inventaire`: the integration pipeline already exists
(`.forgejo/workflows/ci.yml`). The forge's generic registry answers on
`http://localhost:3000/api/packages/apprenant/generic/inventaire/<version>/<file>`.

## Goal (expected state)

1. The `main` `Makefile` has a **`publish`** target that sends the **already
   built** artifact and its `.sha256` file to the registry.
2. The pipeline also triggers on a **`v*` tag**, and calls `make publish` only
   in that case, with `REGISTRE_JETON` passed through
   `env: ${{ secrets.REGISTRE_JETON }}`.
3. No token is written in the repository.
4. The **`v1.0.0`** tag is pushed and its pipeline is **green**: the registry
   holds `inventaire-1.0.0.pyz` and `inventaire-1.0.0.pyz.sha256`.
5. `~/inventaire-1.0.0.pyz` is the artifact **downloaded from the registry**,
   with the same digest.

## Validation

```bash
dsoxlab check artefacts
```
