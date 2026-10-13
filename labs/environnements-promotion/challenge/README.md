# Challenge: environnements-promotion

## Mission

On `forge-1.lab`, in `~/inventaire`. To run an on-demand pipeline: the forge's
**Actions** tab (`ssh -L 3000:localhost:3000 forge-1.lab`, then
`http://localhost:3000`, account `apprenant` / `apprenant-lab`), or the API
`POST /api/v1/repos/apprenant/inventaire/actions/workflows/<file>/dispatches`.

## Goal (expected state)

1. On `main`, a **`workflow_dispatch`** pipeline asks for the **environment**
   and the **version**, accepts an optional **digest**, and calls
   `make deployer`. Inputs go through `env:`,
   never interpolated into `run:`.
2. The `/var/log/inventaire/deploiements.log` journal shows, in this order:
   `1.1.0` to **recette**, then `1.1.0` to **production** with the **same
   digest**, enforced by the `empreinte` input (the journal then carries
   `empreinte-imposee`), then `1.0.0` to **production** (rollback).
3. The installed artifacts are the registry's, installed by the runner.
4. `curl localhost:8081/version` answers `1.1.0` and `recette`;
   `curl localhost:8082/version` answers `1.0.0` and `production`.

## Validation

```bash
dsoxlab check environnements-promotion
```
