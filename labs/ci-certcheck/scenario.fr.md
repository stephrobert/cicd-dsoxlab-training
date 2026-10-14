# Contexte : la CI de certcheck

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
https://blog.stephane-robert.info/docs/developper/pratiques/ci-certcheck/
