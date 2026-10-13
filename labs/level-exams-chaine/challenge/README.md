# Level exam: repair a broken delivery chain

## Mission

On `forge-1.lab`, in `~/inventaire`. The chain delivers, apparently: the `main`
pipeline is green and version `1.0.0` is published. It lies. Make it
**honest**, publish a **corrected version** and **promote** it all the way to
production, then write down what you found. No hints: you have the forge
(`ssh -L 3000:localhost:3000 forge-1.lab`, account `apprenant` /
`apprenant-lab`), the repository and both environments (staging on 8081,
production on 8082).

## Goal (expected state)

1. The integration pipeline only calls `make` targets, masks no failure, pins
   every action to its commit SHA, prints no secret, and only publishes on a
   `v*` tag.
2. `main` is **green**, the `test_compte_par_role` test is untouched: the code
   is what needs fixing.
3. A **new version** is published from a green tag.
4. Deployment installs the published version without rebuilding it, without
   interpolating any input in `run:`; the new version runs in staging then in
   production, **same digest**, enforced for production.
5. `risques.md`, at the repository root on `main`, names the security defects
   found, one per line, with their fix.

## Validation

```bash
dsoxlab check level-exams-chaine
```
