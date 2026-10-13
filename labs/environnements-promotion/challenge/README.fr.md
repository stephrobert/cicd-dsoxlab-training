# Challenge : environnements-promotion

## Mission

Sur `forge-1.lab`, dans `~/inventaire`. Lancer une pipeline à la demande :
onglet **Actions** de la forge (`ssh -L 3000:localhost:3000 forge-1.lab`, puis
`http://localhost:3000`, compte `apprenant` / `apprenant-lab`), ou l'API
`POST /api/v1/repos/apprenant/inventaire/actions/workflows/<fichier>/dispatches`.

## Objectif (état attendu)

1. Sur `main`, une pipeline **`workflow_dispatch`** demande l'**environnement**
   et la **version**, accepte une **empreinte** facultative, et appelle
   `make deployer` sans argument. Les entrées passent par
   `env:` (`DEPLOI_ENV`, `DEPLOI_VERSION`, `DEPLOI_EMPREINTE`), jamais interpolées
   dans `run:` ni passées sur la ligne de commande de `make`.
2. Le journal `/var/log/inventaire/deploiements.log` montre, dans cet ordre :
   `1.1.0` en **recette**, puis `1.1.0` en **production** avec la **même
   empreinte**, imposée par l'entrée `empreinte` (le journal porte alors
   `empreinte-imposee`), puis `1.0.0` en **production** (retour arrière).
3. Les artefacts installés sont ceux du registre, installés par le runner.
4. `curl localhost:8081/version` répond `1.1.0` et `recette` ;
   `curl localhost:8082/version` répond `1.0.0` et `production`.

## Validation

```bash
dsoxlab check environnements-promotion
```
