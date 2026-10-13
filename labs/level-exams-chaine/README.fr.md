# Épreuve de niveau : réparer une chaîne de livraison cassée

## Mission

Sur `forge-1.lab`, dans `~/inventaire`. La chaîne livre, en apparence : la
pipeline de `main` est verte et la version `1.0.0` est publiée. Elle ment.
Rendez-la **honnête**, publiez une **version corrigée** et **promouvez-la**
jusqu'en production, puis écrivez ce que vous avez trouvé. Aucun indice : vous
disposez de la forge (`ssh -L 3000:localhost:3000 forge-1.lab`, compte
`apprenant` / `apprenant-lab`), du dépôt et des deux environnements (recette
sur 8081, production sur 8082).

## Objectif (état attendu)

1. La pipeline d'intégration n'appelle que des cibles `make`, ne masque aucun
   échec, épingle chaque action par le SHA de son commit, n'affiche aucun
   secret, et ne publie que sur une étiquette `v*`.
2. `main` est **verte**, le test `test_compte_par_role` est intact : c'est le
   code qu'il faut corriger.
3. Une **nouvelle version** est publiée depuis une étiquette verte.
4. Le déploiement installe la version publiée sans la reconstruire, sans
   interpoler d'entrée dans `run:` ; la nouvelle version tourne en recette puis
   en production, **même empreinte**, imposée pour la production.
5. `risques.md`, à la racine du dépôt sur `main`, nomme les défauts de
   sécurité trouvés, un par ligne, avec leur correction.

## Validation

```bash
dsoxlab check level-exams-chaine
```
