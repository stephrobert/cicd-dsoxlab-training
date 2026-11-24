# La CI de certcheck

## La situation

`certcheck` signale les certificats TLS d'un parc qui arrivent à expiration.
Son dépôt porte une pipeline, `.forgejo/workflows/ci.yml`, qui rejoue à chaque
push sur `main` et à chaque demande de fusion les contrôles qu'un développeur
lance sur son poste : récupérer le code, préparer Python, installer les
dépendances verrouillées, vérifier la qualité (linter et formatage), lancer
les tests, construire le paquet.

Le dernier commit de `main` a rendu la pipeline **rouge**. Votre travail :
lire le run, comprendre l'étape qui échoue, réparer ; puis provoquer vous-même
deux échecs dans une demande de fusion, un test cassé et un formatage cassé,
pour voir comment la CI les signale, et les corriger.

Méthode dans la leçon compagnon :
https://www.stephane-robert.info/docs/developper/pratiques/ci-certcheck/

## Ce qui est demandé

### Mission

Connectez-vous à la machine (`ssh forge-1.lab`) : le dépôt est cloné dans
`~/certcheck`, la forge répond sur `http://localhost:3000` (compte
`apprenant`, mot de passe `apprenant-lab`). Pour l'ouvrir dans votre
navigateur : `ssh -L 3000:localhost:3000 forge-1.lab`, puis l'onglet
**Actions** du dépôt.

### Objectif (état attendu)

1. La pipeline est **verte** sur le dernier commit de `main` : le défaut du
   commit de départ est réparé.
2. Une **demande de fusion** porte un commit rendu **rouge par un test**,
   suivi d'un commit **vert**.
3. Une **demande de fusion** porte un commit rendu **rouge par le
   formatage**, suivi d'un commit **vert**.
4. La sortie d'une commande de la pipeline, rejouée en local sur un commit
   rouge, est conservée dans `~/echec-local.txt`.
5. `~/reponses-ci.yaml` donne l'ordre des étapes, l'étape qui installe les
   dépendances et l'étape en échec du premier run de `main`.

### Contraintes

- La pipeline fournie ne change pas : on la lit, on ne la réécrit pas.
- On lit l'état de la forge (statuts, demandes de fusion, commits), jamais les
  commandes tapées. La cause d'un commit rouge est recalculée en rejouant ses
  contrôles.

### Validation

```bash
dsoxlab check ci-certcheck
```
