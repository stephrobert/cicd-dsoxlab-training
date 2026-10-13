# Level exam: repair a broken delivery chain

## Mission

On `forge-1.lab`, in `~/inventaire`. The chain delivers, apparently: the `main`
pipeline is green and version `1.0.0` is published. It lies. Make it
**honest**, publish a **corrected version** and **promote** it all the way to
production, then write down what you found. No hints: you have the forge
(`ssh -L 3000:localhost:3000 forge-1.lab`, account `apprenant` /
`apprenant-lab`), the repository and both environments (staging on 8081,
production on 8082).

## Prerequisites

The core lessons of the course, and being able to read then fix a Python
function of a few lines.

## Goal (expected state)

1. The integration pipeline runs `make lint`, `make test` and `make build`,
   in that order, masks no failure, pins every action to its commit SHA, prints
   no secret, and only publishes on a `v*` tag. The leaked token is **revoked**
   and replaced in the `REGISTRE_JETON` secret.
2. `main` is **green**, `tests/test_donnees.py` and the `make test` recipe are
   untouched: the code is what needs fixing (one line of Python), and
   production must count correctly.
3. A **new version** is published from a green tag.
4. Deployment installs the published version without rebuilding it, without
   interpolating any input in `run:` nor passing it on the `make` command
   line; the new version runs in staging then in
   production, **same digest**, enforced for production.
5. `risques.md`, at the repository root on `main`, names the security defects
   found, one per line, with their fix.

## Validation

```bash
dsoxlab check level-exams-chaine
```
