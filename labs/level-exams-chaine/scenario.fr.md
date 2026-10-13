# Contexte : une chaîne qui ment

L'équipe d'`inventaire` a monté sa chaîne vite. La pipeline est verte, une
version est en ligne, tout le monde est content. En la relisant, vous voyez
qu'elle ment : un échec de test est masqué, une étape ne se rejoue pas en local,
le jeton de publication se lit dans le journal, n'importe quelle branche publie,
et le déploiement reconstruit l'artefact au lieu d'installer celui qui a été
testé. C'est l'épreuve de fin du niveau « Comprendre et construire une chaîne
de livraison » : tout ce que la formation a enseigné, sans indice.

Formation : https://blog.stephane-robert.info/docs/pipeline-cicd/
