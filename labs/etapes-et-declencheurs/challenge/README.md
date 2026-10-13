# Challenge: etapes-et-declencheurs

## Mission

Log into the machine (`ssh forge-1.lab`): the repository is cloned in
`~/inventaire`, the forge answers on `http://localhost:3000` (account
`apprenant`, password `apprenant-lab`). To open it in your browser:
`ssh -L 3000:localhost:3000 forge-1.lab`.

## Goal (expected state)

1. On `main`, a `.forgejo/workflows/*.yml` file triggers the pipeline on a
   **push to `main`** and on a **pull request**, with the `debian` runner.
2. Every `run:` step of the pipeline **calls a make target** (`lint`, `test`,
   `build`), and nothing else.
3. The pipeline is **green** on the latest `main` commit.
4. An **open pull request** carries a commit with a broken test: its pipeline
   is **red**.
5. The output of `make test`, run locally on that commit, is kept in
   `~/echec-local.txt`.

## Constraints

- Every action used is pinned to its commit SHA.
- The forge state is read (files, statuses, pull requests), never the commands
  typed.

## Validation

```bash
dsoxlab check etapes-et-declencheurs
```
