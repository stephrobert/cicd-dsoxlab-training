# Contexte : promouvoir le même artefact, puis revenir en arrière

Deux versions d'`inventaire` sont publiées dans le registre de la forge :
`1.0.0` et `1.1.0`. Deux environnements attendent sur `forge-1.lab` :
**recette** (port 8081) et **production** (port 8082). Ils exécutent le même
fichier `.pyz` ; seule leur **configuration** change
(`/etc/inventaire/<environnement>.env`).

Le dépôt fournit `scripts/deployer.sh` et la cible `make deployer` : ils
téléchargent une version **publiée**, vérifient son **empreinte**, l'installent
et contrôlent que l'environnement sert la bonne version. Seul le **runner**
peut installer un artefact : on ne déploie que **par la pipeline**.

Vous écrivez la pipeline de déploiement **à la demande** (le geste
d'approbation), déployez `1.1.0` en recette, la **promouvez** en production
sans la reconstruire, puis faites un **retour arrière** de la production vers
`1.0.0`.

Méthode dans la leçon compagnon :
https://blog.stephane-robert.info/docs/pipeline-cicd/fondamentaux/environnements-promotion/
