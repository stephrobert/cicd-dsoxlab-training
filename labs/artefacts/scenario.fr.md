# Contexte : construire une fois, publier, retrouver par l'empreinte

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
https://blog.stephane-robert.info/docs/pipeline-cicd/fondamentaux/artefacts/
