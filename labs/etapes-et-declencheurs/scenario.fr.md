# Contexte : des étapes dans le dépôt, une pipeline qui les orchestre

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
