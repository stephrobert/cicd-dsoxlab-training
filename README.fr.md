# Formation CI/CD : le modèle avant l'outil

**Langue :** [English](./README.md) · [Français](./README.fr.md)

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

Les labs de la formation
[Introduction aux pipelines CI/CD : le modèle avant l'outil](https://blog.stephane-robert.info/docs/pipeline-cicd/)
du blog, joués avec [dsoxlab](https://github.com/stephrobert/dsoxlab).

## Ce que c'est

**Cinq labs, une forge, aucun compte en ligne.** Tout se joue sur une forge
locale que le lab installe dans la machine virtuelle `forge-1.lab` : Forgejo
16.0.6 et Forgejo Runner 13.2.0, exécuteur `host`. Le dépôt fil rouge,
`inventaire`, est un petit service Python sans dépendance.

L'ordre de la formation est délibéré : les étapes d'abord, puis les artefacts,
puis la promotion. Vous écrivez une cible `make` avant d'écrire une pipeline,
pour que la pipeline n'ait rien d'autre à dire que `make lint test build`. Une
chaîne qui ne marche que dans un seul produit de CI vous a appris ce produit,
pas la livraison.

Les labs sont notés sur l'état laissé dans la forge et sur la machine, **jamais
sur les commandes tapées**.

## Prérequis

- **Python 3.11+ et [`uv`](https://docs.astral.sh/uv/)**
- **`git`**
- **Un hyperviseur**, puisque tous les labs d'ici sont `runtime: vm` : soit
  **libvirt/KVM** (avec `terraform` et le provider `dmacvicar/libvirt`), soit
  **Incus**. Le provider est déclaré en liste dans [`meta.yml`](./meta.yml), et
  vous en choisissez un avec `dsoxlab use --provider`.
- **Environ 2 Go de RAM libre** pour la machine unique, `forge-1.lab`.
- **Un accès réseau sortant** au premier provision, pour récupérer l'image de
  base et les versions de Forgejo.

`dsoxlab doctor` dit ce dont ce dépôt a besoin et ce dont il n'a pas besoin, et
distingue un contrôle qui a échoué d'un contrôle qu'il n'a pas pu mesurer.

## Installation

`dsoxlab` est publié sur [PyPI](https://pypi.org/project/dsoxlab/).
Installez-le en outil autonome, pour qu'il reste hors de ce dépôt :

```bash
# 1. La CLI dsoxlab (outil externe, hors de ce dépôt)
uv tool install dsoxlab

# 2. Ce catalogue de labs
git clone https://github.com/stephrobert/cicd-dsoxlab-training.git
cd cicd-dsoxlab-training

# 3. Vérifier le contrat et la machine
dsoxlab validate-structure
dsoxlab doctor
```

### Votre premier lab, en cinq minutes

La machine doit exister d'abord : contrairement aux catalogues `shell`, rien
ici ne tourne sur votre propre poste.

```bash
dsoxlab use --provider incus         # ou kvm
dsoxlab provision                    # crée forge-1.lab (~5 min la première fois)

dsoxlab run       etapes-et-declencheurs
dsoxlab challenge etapes-et-declencheurs
ssh forge-1.lab                      # vous travaillez sur la machine
dsoxlab check     etapes-et-declencheurs

dsoxlab destroy                      # quand vous avez fini pour la journée
```

`provision` sort en code non nul si un hôte ne répond pas, et nomme les
domaines orphelins qu'il a laissés plutôt que d'annoncer un succès. Un `check`
joué sur un lab jamais démarré ne mesure rien, et le dit au lieu d'enregistrer
un 0.

### Garder à jour

```bash
uv tool upgrade dsoxlab        # le moteur, publié sur PyPI
git -C <ce dépôt> pull         # le catalogue
```

Le moteur et le catalogue avancent indépendamment : un nouveau `dsoxlab` ne
demande jamais de recloner les labs, et de nouveaux labs ne demandent jamais de
mettre l'outil à jour, tant que la version du contrat correspond.

## Comment ça marche

### Le contrat déclaratif, à deux niveaux

Le catalogue est décrit par des données, pas par du code, et c'est ce qui garde
le moteur `dsoxlab` indépendant du domaine :

- **`meta.yml`** à la racine déclare l'identité du dépôt, l'**infrastructure**
  (provider, réseau `lab-cicd`, `10.10.90.0/24`, et l'hôte unique
  `forge-1.lab`) et l'**ordre** des sections affichées par `list-labs` ;
- **`lab.yaml`** par lab déclare ses `skills`, son `level`, son `runtime` (type
  et targets), ses `distros`, son `doc_url` et un bloc `validation`. Un
  `lab.fr.yaml` surcharge `title` et `description` en français, et rien
  d'autre.

Les gabarits Terraform et cloud-init sont **packagés dans dsoxlab**, pas ici :
ce dépôt ne déclare que son bloc `infra:` et sa clé publique dans `ssh/`.

`dsoxlab validate-structure` contrôle tout le contrat : `meta.yml` bien formé,
chaque lab référencé présent avec un `lab.yaml` valide, chaque `host` nommé par
un lab réellement présent dans `infra.hosts[]`, et chaque lien relatif d'un
README qui mène quelque part.

### Le cycle de vie d'un lab

```bash
dsoxlab list-labs              # parcourir le catalogue
dsoxlab show      <id>         # métadonnées et état d'un lab
dsoxlab run       <id>         # poser l'état de départ
dsoxlab challenge <id>         # lire la mission, sans pas-à-pas
dsoxlab hint      <id>         # révéler un indice (déduit du score)
dsoxlab check     <id>         # lancer les tests, calculer et enregistrer le score
dsoxlab clean     <id>         # défaire ce que le lab a posé
dsoxlab progress               # avancement par section, score moyen
```

### Les runtimes

| Runtime | Ce que le lab demande |
|---|---|
| `vm` | la machine `forge-1.lab`, provisionnée par `dsoxlab provision`, sous Debian 13. Le lab y installe Forgejo et son runner, et les tests interrogent la forge et le système. |

Les cinq labs sont `vm`, et aucun ne déclare `runtime.services` : il n'y a
aucun conteneur à démarrer, la forge vit dans la machine.

### Le modèle de validation

La validation **prouve l'état, elle ne fait pas confiance à l'apprenant**.
Chaque lab porte des tests `pytest` + `pytest-testinfra` sous
`challenge/tests/` qui demandent à la forge et à la machine ce qu'elles
contiennent vraiment : la pipeline qui a tourné, l'artefact publié sous son
empreinte, l'environnement où une version a été promue.

Et un lab est prouvé **dans les deux sens** : les tests doivent échouer avant
le travail et passer après. Un test vert avant le travail n'est pas un test,
c'est une hypothèse sur le setup. `scripts/valider-labs.py` joue ce cycle
entier sur chaque lab et écrit son verdict dans
[`validation-labs.json`](./validation-labs.json), qui est versionné : un lab
livré sans verdict ne prouve rien.

Les solutions de référence vivent sous `solution/`, **chiffrées avec
ansible-vault** : une solution livrée en clair gâche le lab, et git la garde
pour toujours.

### Score, indices, avancement

`check` enregistre un score (tests réussis sur total, moins le coût des indices
révélés). Les indices sont **en base64** dans `challenge/hints.yaml`, pour qu'on
n'y accède pas en ouvrant le fichier, et leur coût croît avec leur précision.
L'historique vit dans une base SQLite **locale à ce dépôt**.

Une exécution qui n'a rien mesuré n'est ni une réussite ni un échec : si tous
les tests collectés skippent, `check` n'enregistre aucune note et dit pourquoi.
Un 0 accuserait le lab de ce qui manque au poste, qui est ici le plus souvent
`forge-1.lab` qui n'est pas debout.

## Catalogue

Les labs vivent sous `labs/` et sont ordonnés par `meta.yml`. Le tableau ci-dessous est généré depuis les vrais `lab.yaml`, leurs titres et leurs guides compagnons : `python3 scripts/gen_catalog.py` le régénère.

<!-- LABS:START -->
### Une première CI, pour Développer pour les Ops

Lire la pipeline fournie avec `certcheck`, un petit outil Python (dépendances, qualité, tests, paquet), réparer `main`, puis faire échouer un test et le formatage dans une demande de fusion, rejouer l'échec en local et corriger.

| Lab (id) | Titre | Niveau | Runtime | Guide compagnon |
|---|---|---|---|---|
| `ci-certcheck` | La CI de certcheck : six étapes, un run rouge, une correction | o1 | vm | [guide](https://blog.stephane-robert.info/docs/developper/pratiques/ci-certcheck/) |

### Le modèle avant l'outil

Écrire une cible `make`, puis une pipeline qui n'appelle que `make lint test build`, verte sur `main` et rouge sur un test cassé dans une demande de fusion, avec l'échec rejoué en local. Puis publier l'artefact sur une étiquette `v*` avec un jeton dédié gardé en secret, le retrouver par son empreinte SHA-256, et promouvoir **cette même empreinte** de la recette à la production avant de revenir en arrière.

| Lab (id) | Titre | Niveau | Runtime | Guide compagnon |
|---|---|---|---|---|
| `etapes-et-declencheurs` | Des étapes dans le dépôt, une pipeline qui les orchestre | c1 | vm | [guide](https://blog.stephane-robert.info/docs/pipeline-cicd/fondamentaux/etapes-et-declencheurs/) |
| `artefacts` | Construire une fois, publier, retrouver par l'empreinte | c1 | vm | [guide](https://blog.stephane-robert.info/docs/pipeline-cicd/fondamentaux/artefacts/) |
| `environnements-promotion` | Promouvoir le même artefact de la recette à la production, puis revenir en arrière | c1 | vm | [guide](https://blog.stephane-robert.info/docs/pipeline-cicd/fondamentaux/environnements-promotion/) |

### Épreuve de niveau

Sans indice : rendre honnête et verte une chaîne qui ment, publier une version corrigée, la promouvoir par empreinte en production, et lister les risques trouvés.

| Lab (id) | Titre | Niveau | Runtime | Guide compagnon |
|---|---|---|---|---|
| `level-exams-chaine` | Épreuve de niveau : réparer une chaîne de livraison cassée | c1 | vm | [guide](https://blog.stephane-robert.info/docs/pipeline-cicd/fondamentaux/epreuve-chaine-cassee/) |

_5 labs, table générée par `scripts/gen_catalog.py`._
<!-- LABS:END -->
## Contribuer

Un lab est prouvé **dans les deux sens** avant d'être fusionné,
`dsoxlab validate-structure` est vert, et l'énoncé existe en anglais et en
français.

Tout ce qui s'affiche est bilingue. Un document traduit d'un seul côté est
signalé par le validateur, et non laissé à la bonne volonté.

## Licence

Voir [`LICENSE`](./LICENSE).
