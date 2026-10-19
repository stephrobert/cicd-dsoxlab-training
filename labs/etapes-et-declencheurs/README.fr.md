# Lab : des étapes dans le dépôt, une pipeline qui les orchestre

Leçon compagnon :
[Étapes et déclencheurs](https://www.stephane-robert.info/docs/pipeline-cicd/fondamentaux/etapes-et-declencheurs/).

La machine `forge-1.lab` porte une forge **Forgejo** et son **runner**
(exécuteur `host`, label `debian`). Le dépôt `apprenant/inventaire` y est
poussé et cloné dans `~/inventaire`.

```bash
dsoxlab run etapes-et-declencheurs     # pose l'état de départ
ssh forge-1.lab                        # puis travaillez dans ~/inventaire
dsoxlab challenge etapes-et-declencheurs
dsoxlab check etapes-et-declencheurs
```
