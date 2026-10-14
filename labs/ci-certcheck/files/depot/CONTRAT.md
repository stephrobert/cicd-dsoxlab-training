# Contrat de certcheck, version de base

Ce document dit ce que **certcheck** doit faire, vu de l'extérieur. Il est
vérifié en **boîte noire**, en lançant `bin/certcheck` comme le feraient cron
ou un pipeline. La publication sur la forge n'en fait pas encore partie :
elle vient avec le lab `appeler-une-api`.

## Entrée : l'inventaire

Un fichier texte, une ligne par hôte : le nom de l'hôte, puis le chemin du
certificat PEM collecté sur cet hôte, séparés par des **espaces ou des
tabulations**. Un chemin relatif se résout depuis le **dossier de
l'inventaire**. Les lignes vides et celles qui commencent par `#` sont
ignorées.

```text
# hôte    certificat collecté
web-01    certs/web-01.pem
vpn-01	certs/vpn-01.pem
```

## Ligne de commande

| Option | Effet |
|---|---|
| `--inventory FICHIER` | l'inventaire à lire, `inventaire.txt` par défaut |
| `--days N` | le seuil d'alerte, en jours (entier positif) |
| `--format text\|json` | le format de la sortie standard, `text` par défaut |
| `--version` | affiche `certcheck X.Y.Z` et sort en 0 |
| `--help` | l'aide, qui cite chaque option, sur la sortie standard, et sort en 0 |

Une option inconnue ou une valeur invalide (`--days abc`, `--format xml`)
écrit un message sur la **sortie d'erreur** et sort en **2**, sans rien écrire
sur la sortie standard.

## Configuration par l'environnement

| Variable | Rôle | Défaut |
|---|---|---|
| `CERTCHECK_DAYS` | le seuil, si `--days` est absent | `30` |
| `CERTCHECK_NOW` | la date du jour, `AAAA-MM-JJ` (pour les tests, déjà écrite) | la date du jour, en UTC |

L'option l'emporte toujours sur la variable, la variable sur le défaut. Une
valeur invalide de `CERTCHECK_DAYS` sort en 2, message sur la sortie
d'erreur.

## Décision

Pour chaque certificat, `days_left` est le nombre de jours entre la date du
jour et la **date** d'expiration (`notAfter`, en UTC) :

| Statut | Condition |
|---|---|
| `expired` | `days_left < 0` |
| `warning` | `0 <= days_left <= seuil` (le seuil est **inclusif**) |
| `ok` | `days_left > seuil` |
| `error` | certificat absent ou illisible |

## Sorties

- **`--format text`** : une ligne par hôte, qui contient au moins le nom de
  l'hôte et son statut.
- **`--format json`** : un seul document JSON sur la sortie standard, rien
  d'autre :

```json
{
  "threshold_days": 30,
  "certificates": [
    {"host": "web-01", "not_after": "2045-06-15", "days_left": 6819, "status": "ok"},
    {"host": "web-03", "not_after": null, "days_left": null, "status": "error"}
  ]
}
```

- Les **journaux et messages d'erreur** vont sur la **sortie d'erreur** : un
  certificat illisible y est signalé par le nom de son hôte.

## Codes de sortie

| Code | Sens |
|---|---|
| 0 | tous les certificats sont `ok` |
| 1 | au moins un certificat `warning` ou `expired`, aucun `error` |
| 2 | usage incorrect, configuration invalide, inventaire ou certificat inexploitable |
