# Lab : la CI de certcheck, six étapes, un run rouge, une correction

Leçon compagnon, dans la formation **Développer pour les Ops** :
[La CI de certcheck](https://blog.stephane-robert.info/docs/developper/pratiques/ci-certcheck/).

La machine `forge-1.lab` porte une forge **Forgejo**, son **runner**
(exécuteur `host`, label `debian`) et **uv**. Le dépôt `apprenant/certcheck`,
un petit outil Python d'exploitation, y est poussé avec sa pipeline et cloné
dans `~/certcheck`. On n'écrit pas de pipeline : on lit celle qui est fournie,
on répare un run rouge, puis on fait échouer exprès un test et le formatage
pour voir ce que la CI en dit.

```bash
dsoxlab run ci-certcheck          # pose l'état de départ (main est rouge)
ssh forge-1.lab                   # puis travaillez dans ~/certcheck
dsoxlab challenge ci-certcheck
dsoxlab check ci-certcheck
```

Durée : environ 30 minutes. Noté sur l'état de la forge et de la machine.
