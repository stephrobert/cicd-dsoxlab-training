# Des étapes dans le dépôt, une pipeline qui les orchestre

## La situation

Votre équipe livre `inventaire`, un petit service Python qui sert la liste de
ses serveurs. Le dépôt a des tests et un `Makefile` (`make lint`, `make test`,
`make build`), mais aucune pipeline : rien ne vérifie un changement avant qu'il
arrive sur `main`.

La forge de l'équipe est une instance **Forgejo** locale, avec son **runner**,
dans la machine `forge-1.lab`. Vous y écrivez la pipeline, sans recopier les
commandes du `Makefile` : elle ne fait que **l'appeler**, pour qu'un échec en
CI se reproduise à l'identique sur votre poste.

Méthode dans la leçon compagnon :
https://www.stephane-robert.info/docs/pipeline-cicd/fondamentaux/etapes-et-declencheurs/

## Ce qui est demandé

### Mission

Connectez-vous à la machine (`ssh forge-1.lab`) : le dépôt est cloné dans
`~/inventaire`, la forge répond sur `http://localhost:3000` (compte
`apprenant`, mot de passe `apprenant-lab`). Pour l'ouvrir dans votre
navigateur : `ssh -L 3000:localhost:3000 forge-1.lab`.

### Objectif (état attendu)

1. Sur `main`, un fichier `.forgejo/workflows/*.yml` déclenche la pipeline sur
   un **push vers `main`** et sur une **demande de fusion**, avec le runner
   `debian`.
2. Chaque étape `run:` de la pipeline **appelle une cible make** (`lint`,
   `test`, `build`), et rien d'autre.
3. La pipeline est **verte** sur le dernier commit de `main`.
4. Une **demande de fusion ouverte** porte un commit dont un test casse : sa
   pipeline est **rouge**.
5. La sortie de `make test`, lancée en local sur ce commit, est conservée dans
   `~/echec-local.txt`.

### Contraintes

- Toute action utilisée est épinglée par le SHA de son commit.
- On lit l'état de la forge (fichiers, statuts, demandes de fusion), jamais
  les commandes tapées.

### Validation

```bash
dsoxlab check etapes-et-declencheurs
```
