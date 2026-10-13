# Lab: stages in the repository, a pipeline that orchestrates them

Companion lesson (in French):
[Étapes et déclencheurs](https://blog.stephane-robert.info/docs/pipeline-cicd/fondamentaux/etapes-et-declencheurs/).

The `forge-1.lab` machine runs a **Forgejo** forge and its **runner** (`host`
executor, `debian` label). The `apprenant/inventaire` repository is pushed
there and cloned in `~/inventaire`.

```bash
dsoxlab run etapes-et-declencheurs     # sets the starting state
ssh forge-1.lab                        # then work in ~/inventaire
dsoxlab challenge etapes-et-declencheurs
dsoxlab check etapes-et-declencheurs
```
