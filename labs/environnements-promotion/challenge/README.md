# Promote the same artifact, then roll back

## The situation

Two versions of `inventaire` are published in the forge registry: `1.0.0` and
`1.1.0`. Two environments wait on `forge-1.lab`: **staging** (`recette`, port
8081) and **production** (port 8082). They run the same `.pyz` file; only
their **configuration** differs (`/etc/inventaire/<environment>.env`).

The repository provides `scripts/deployer.sh` and the `make deployer` target:
they download a **published** version, check its **digest**, install it and
check the environment serves the right version. Only the **runner** can install
an artifact: deployments go **through the pipeline** only.

You write the **on-demand** deployment pipeline (the approval gesture), deploy
`1.1.0` to staging, **promote** it to production without rebuilding it, then
**roll production back** to `1.0.0`.

Companion lesson (in French):
https://www.stephane-robert.info/en/docs/devsecops/delivery/environments-and-promotion/

## What is asked

### Mission

On `forge-1.lab`, in `~/inventaire`. To run an on-demand pipeline: the forge's
**Actions** tab (`ssh -L 3000:localhost:3000 forge-1.lab`, then
`http://localhost:3000`, account `apprenant` / `apprenant-lab`), or the API
`POST /api/v1/repos/apprenant/inventaire/actions/workflows/<file>/dispatches`.

### Goal (expected state)

1. On `main`, a **`workflow_dispatch`** pipeline asks for the **environment**
   and the **version**, accepts an optional **digest**, and calls
   `make deployer` with no argument. Inputs go through `env:` (`DEPLOI_ENV`,
   `DEPLOI_VERSION`, `DEPLOI_EMPREINTE`), never on the `make` command line,
   never interpolated into `run:`.
2. The `/var/log/inventaire/deploiements.log` journal shows, in this order:
   `1.1.0` to **recette**, then `1.1.0` to **production** with the **same
   digest**, enforced by the `empreinte` input (the journal then carries
   `empreinte-imposee`), then `1.0.0` to **production** (rollback).
3. The installed artifacts are the registry's, installed by the runner.
4. `curl localhost:8081/version` answers `1.1.0` and `recette`;
   `curl localhost:8082/version` answers `1.0.0` and `production`.

### Validation

```bash
dsoxlab check environnements-promotion
```
