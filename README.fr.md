# cicd-dsoxlab-training

Les labs de la formation **Introduction aux pipelines CI/CD : le modèle avant
l'outil** du blog : <https://blog.stephane-robert.info/docs/pipeline-cicd/>.

Tous les labs se jouent **sans aucun compte en ligne**, sur une forge locale
(Forgejo 16.0.6 et Forgejo Runner 13.2.0, exécuteur `host`) que le lab installe
dans la VM `forge-1.lab`. Le dépôt fil rouge, `inventaire`, est un petit
service Python sans dépendance.

| Lab | Ce que vous faites |
|---|---|
| `etapes-et-declencheurs` | écrire une cible `make`, puis une pipeline qui n'appelle que `make lint test build`, verte sur `main`, rouge sur un test cassé dans une demande de fusion, échec rejoué en local |
| `artefacts` | publier sur une étiquette `v*` l'artefact construit et testé par la pipeline, avec un jeton dédié gardé en secret, puis le retrouver par son empreinte SHA-256 |
| `environnements-promotion` | déployer une version publiée en recette, promouvoir exactement la même empreinte en production, puis revenir en arrière |

```bash
uv tool install dsoxlab                 # ou : uv tool upgrade dsoxlab
dsoxlab use --provider incus            # ou kvm
dsoxlab provision
dsoxlab run etapes-et-declencheurs
ssh forge-1.lab
dsoxlab check etapes-et-declencheurs
dsoxlab destroy
```

Les labs sont notés sur l'état laissé dans la forge et sur la machine, jamais
sur les commandes tapées. Chaque lab est attesté dans les deux sens (0 avant le
travail, 100 avec la solution de référence) par `scripts/valider-labs.py`,
verdicts dans `validation-labs.json`.
