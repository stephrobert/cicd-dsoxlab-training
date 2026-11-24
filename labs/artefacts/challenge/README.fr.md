# Construire une fois, publier, retrouver par l'empreinte

## La situation

La pipeline d'`inventaire` construit `dist/inventaire-<version>.pyz` à chaque
changement, puis le jette : chaque environnement devrait donc le
reconstruire, et rien ne garantit qu'il obtiendrait le même fichier.

Vous publiez l'artefact que la pipeline vient de **construire et de tester**,
une seule fois par version, dans le **registre de paquets** de la forge. La
publication n'a lieu que sur une **étiquette de version** (`v1.0.0`), avec un
jeton **dédié** que la forge garde en **secret** (`REGISTRE_JETON`, déjà créé).
Puis vous retrouvez la version publiée et la vérifiez par son **empreinte
SHA-256**.

Méthode dans la leçon compagnon :
https://www.stephane-robert.info/docs/pipeline-cicd/fondamentaux/artefacts/

## Ce qui est demandé

### Mission

Sur `forge-1.lab`, dans `~/inventaire` : la pipeline d'intégration existe déjà
(`.forgejo/workflows/ci.yml`). Le registre générique de la forge répond sur
`http://localhost:3000/api/packages/apprenant/generic/inventaire/<version>/<fichier>`.

### Objectif (état attendu)

1. Le `Makefile` de `main` a une cible **`publish`** qui envoie au registre
   l'artefact **déjà construit** et son fichier `.sha256`.
2. La pipeline se déclenche aussi sur une **étiquette `v*`**, et n'appelle
   `make publish` que dans ce cas, avec `REGISTRE_JETON` passé par
   `env: ${{ secrets.REGISTRE_JETON }}`.
3. Aucun jeton n'est écrit dans le dépôt.
4. L'étiquette **`v1.0.0`** est poussée et sa pipeline est **verte** : le
   registre porte `inventaire-1.0.0.pyz` et `inventaire-1.0.0.pyz.sha256`.
5. `~/inventaire-1.0.0.pyz` est l'artefact **téléchargé depuis le registre**,
   d'empreinte identique.

### Validation

```bash
dsoxlab check artefacts
```
