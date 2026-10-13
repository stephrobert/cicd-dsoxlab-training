# Context: promote the same artifact, then roll back

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
https://blog.stephane-robert.info/docs/pipeline-cicd/fondamentaux/environnements-promotion/
