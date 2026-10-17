# CI/CD Training: the model before the tool

**Language:** [English](./README.md) · [Français](./README.fr.md)

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

The labs of the blog's course
[Introduction aux pipelines CI/CD : le modèle avant l'outil](https://blog.stephane-robert.info/docs/pipeline-cicd/)
(in French), played with [dsoxlab](https://github.com/stephrobert/dsoxlab).

## What it is

**Five labs, one forge, no online account.** Everything runs on a local forge
that the lab installs inside the `forge-1.lab` virtual machine: Forgejo 16.0.6
and Forgejo Runner 13.2.0 with the `host` executor. The common thread is
`inventaire`, a small Python service with no dependency.

The order of the course is deliberate: stages first, then artifacts, then
promotion. You write a `make` target before you write a pipeline, so that the
pipeline has nothing to say but `make lint test build`. A chain that only works
inside one CI product has taught you that product, not delivery.

Labs are graded on the state left in the forge and on the machine, **never on
the commands typed**.

## Requirements

- **Python 3.11+ and [`uv`](https://docs.astral.sh/uv/)**
- **`git`**
- **A hypervisor**, because every lab here is `runtime: vm`: either
  **libvirt/KVM** (with `terraform` and the `dmacvicar/libvirt` provider) or
  **Incus**. The provider is declared as a list in
  [`meta.yml`](./meta.yml), and you pick one with `dsoxlab use --provider`.
- **About 2 GB of free RAM** for the single machine, `forge-1.lab`.
- **Outbound network access** on first provision, to pull the base image and
  the Forgejo releases.

`dsoxlab doctor` says what this repository needs and what it does not, and
tells apart a check that failed from one it could not measure.

## Install

`dsoxlab` is published on [PyPI](https://pypi.org/project/dsoxlab/). Install it
as a standalone tool, so it stays out of this repository:

```bash
# 1. The dsoxlab CLI (external tool, stays out of this repo)
uv tool install dsoxlab

# 2. This lab catalog
git clone https://github.com/stephrobert/cicd-dsoxlab-training.git
cd cicd-dsoxlab-training

# 3. Check the contract and the machine
dsoxlab validate-structure
dsoxlab doctor
```

### Your first lab, in five minutes

The machine has to exist first: unlike the shell catalogs, nothing here runs on
your own host.

```bash
dsoxlab use --provider incus         # or kvm
dsoxlab provision                    # creates forge-1.lab (~5 min the first time)

dsoxlab run       etapes-et-declencheurs
dsoxlab challenge etapes-et-declencheurs
ssh forge-1.lab                      # you work on the machine
dsoxlab check     etapes-et-declencheurs

dsoxlab destroy                      # when you are done for the day
```

`provision` exits non-zero if a host does not answer, and names the orphan
domains it left behind rather than claiming success. Running `check` on a lab
you never started measures nothing, and says so rather than recording a 0.

### Keeping it up to date

```bash
uv tool upgrade dsoxlab        # the engine, published on PyPI
git -C <this repo> pull        # the catalog
```

The engine and the catalog move independently: a new `dsoxlab` never requires
re-cloning the labs, and new labs never require upgrading the tool, as long as
the contract version matches.

## How it works

### The declarative contract (two levels)

The catalog is described by data, not code, which is what keeps the `dsoxlab`
engine domain-agnostic:

- **`meta.yml`** at the root declares the repository identity, the
  **infrastructure** (provider, network `lab-cicd`, `10.10.90.0/24`, and the
  single host `forge-1.lab`) and the **order** of the sections shown by
  `list-labs`;
- **`lab.yaml`** per lab declares its `skills`, `level`, `runtime` (type and
  targets), `distros`, `doc_url` and a `validation` block. A `lab.fr.yaml`
  overrides `title` and `description` in French, and nothing else.

The Terraform and cloud-init templates are **packaged inside dsoxlab**, not
here: this repository declares only its `infra:` block and its public key in
`ssh/`.

`dsoxlab validate-structure` checks the whole contract: `meta.yml` is well
formed, every referenced lab exists with a valid `lab.yaml`, every `host` named
by a lab really exists in `infra.hosts[]`, and every relative link in a README
leads somewhere.

### The lab lifecycle

```bash
dsoxlab list-labs              # browse the catalog
dsoxlab show      <id>         # metadata and status of one lab
dsoxlab run       <id>         # set the starting state
dsoxlab challenge <id>         # read the mission, no step-by-step
dsoxlab hint      <id>         # reveal a hint (deducted from the score)
dsoxlab check     <id>         # run the tests, compute and record the score
dsoxlab clean     <id>         # undo what the lab set up
dsoxlab progress               # per-section progress, average score
```

### Runtimes

| Runtime | What the lab asks for |
|---|---|
| `vm` | the `forge-1.lab` machine, provisioned by `dsoxlab provision`, on Debian 13. The lab installs Forgejo and its runner there, and the tests query the forge and the system. |

All five labs are `vm`, and none of them declares `runtime.services`: there is
no container to start, the forge lives in the machine.

### The validation model

Validation **proves the state, it does not trust the learner**. Each lab ships
`pytest` + `pytest-testinfra` tests under `challenge/tests/` that ask the forge
and the machine what they actually hold: the pipeline that ran, the artifact
published under its digest, the environment a version was promoted to.

And a lab is proven **in both directions**: the tests must fail before the work
and pass after it. A test that is green before the work is not a test, it is an
assumption about the setup. `scripts/valider-labs.py` plays that whole cycle on
every lab and writes its verdict to
[`validation-labs.json`](./validation-labs.json), which is versioned: a lab
shipped without a verdict proves nothing.

Reference solutions live under `solution/`, **encrypted with ansible-vault**: a
solution shipped in clear text spoils the lab, and git keeps it forever.

### Scoring, hints, progress

`check` records a score (tests passed out of total, minus the cost of any hints
revealed). Hints are **base64-encoded** in `challenge/hints.yaml`, so that
opening the file does not give them away, and their cost grows with their
precision. History lives in a SQLite database **local to this repository**.

A run that measured nothing is neither a pass nor a failure: if every collected
test skips, `check` records no score and says why. A score of 0 would accuse the
lab of what is missing from the machine, which here is usually `forge-1.lab`
not being up.

## Catalog

### A first CI, for Development for Ops

| Lab (id) | Title | Level | Runtime | Companion guide |
|---|---|---|---|---|
| `ci-certcheck` | certcheck's CI: six stages, a red run, a fix | o1 | vm | [guide](https://blog.stephane-robert.info/docs/developper/pratiques/ci-certcheck/) (in French) |

Read the pipeline shipped with `certcheck`, a small Python tool (dependencies,
quality, tests, package), repair `main`, then make a test and the formatting
fail in a pull request, replay the failure locally and fix it.

### The model before the tool

| Lab (id) | Title | Level | Runtime | Companion guide |
|---|---|---|---|---|
| `etapes-et-declencheurs` | Stages in the repository, a pipeline that orchestrates them | c1 | vm | [guide](https://blog.stephane-robert.info/docs/pipeline-cicd/fondamentaux/etapes-et-declencheurs/) (in French) |
| `artefacts` | Build once, publish, find it again by its digest | c1 | vm | [guide](https://blog.stephane-robert.info/docs/pipeline-cicd/fondamentaux/artefacts/) (in French) |
| `environnements-promotion` | Promote the same artifact from staging to production, then roll back | c1 | vm | [guide](https://blog.stephane-robert.info/docs/pipeline-cicd/fondamentaux/environnements-promotion/) (in French) |

Write a `make` target, then a pipeline that only calls `make lint test build`,
green on `main` and red on a broken test in a pull request, with the failure
replayed locally. Then publish the artifact on a `v*` tag with a dedicated
token kept as a secret, find it again by its SHA-256 digest, and promote **that
same digest** from staging to production before rolling back.

### Level exam

| Lab (id) | Title | Level | Runtime | Companion guide |
|---|---|---|---|---|
| `level-exams-chaine` | Level exam: repair a broken delivery chain | c1 | vm | [guide](https://blog.stephane-robert.info/docs/pipeline-cicd/fondamentaux/epreuve-chaine-cassee/) (in French) |

No hints: make a lying chain honest and green, publish a corrected version,
promote it by digest to production, and list the risks you found.

_5 labs. This catalog has no `scripts/gen_catalog.py` yet, so this table is
maintained by hand: check it against `dsoxlab list-labs` when you add a lab._

## Contributing

A lab is proven **in both directions** before it is merged,
`dsoxlab validate-structure` is green, and the statement exists in English and
in French.

Anything user-facing is bilingual. A document translated on one side only is
reported by the validator, not left to goodwill.

## License

See [`LICENSE`](./LICENSE).
