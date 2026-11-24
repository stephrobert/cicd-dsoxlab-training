# Certcheck's CI

## The situation

`certcheck` reports the TLS certificates of a fleet that are about to expire.
Its repository carries a pipeline, `.forgejo/workflows/ci.yml`, which replays
on every push to `main` and every pull request the checks a developer runs on
their workstation: fetch the code, prepare Python, install the locked
dependencies, check quality (linter and formatting), run the tests, build the
package.

The latest `main` commit turned the pipeline **red**. Your job: read the run,
understand the failing stage, repair it; then cause two failures yourself in
a pull request, a broken test and broken formatting, to see how the CI
reports them, and fix them.

Method in the companion lesson (in French):
https://www.stephane-robert.info/docs/developper/pratiques/ci-certcheck/ (in French)

## What is asked

### Mission

Log into the machine (`ssh forge-1.lab`): the repository is cloned in
`~/certcheck`, the forge answers on `http://localhost:3000` (account
`apprenant`, password `apprenant-lab`). To open it in your browser:
`ssh -L 3000:localhost:3000 forge-1.lab`, then the repository's **Actions**
tab.

### Goal (expected state)

1. The pipeline is **green** on the latest `main` commit: the starting
   commit's defect is repaired.
2. A **pull request** carries a commit turned **red by a test**, followed by
   a **green** commit.
3. A **pull request** carries a commit turned **red by formatting**, followed
   by a **green** commit.
4. The output of a pipeline command, replayed locally on a red commit, is
   kept in `~/echec-local.txt`.
5. `~/reponses-ci.yaml` gives the order of the stages, the stage that
   installs the dependencies and the failing stage of `main`'s first run.

### Constraints

- The provided pipeline does not change: you read it, you do not rewrite it.
- The state of the forge is read (statuses, pull requests, commits), never
  the commands typed. The cause of a red commit is recomputed by replaying
  its checks.

### Validation

```bash
dsoxlab check ci-certcheck
```
