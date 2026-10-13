# cicd-dsoxlab-training

Labs for the blog's course **Introduction to CI/CD pipelines: the model before
the tool** (in French): <https://blog.stephane-robert.info/docs/pipeline-cicd/>.

Every lab runs **without any online account**, on a local forge (Forgejo
16.0.6 and Forgejo Runner 13.2.0, `host` executor) installed by the lab inside
the `forge-1.lab` VM. The common-thread repository, `inventaire`, is a small
Python service with no dependency.

| Lab | What you do |
|---|---|
| `etapes-et-declencheurs` | write a `make` target, then a pipeline that only calls `make lint test build`, green on `main`, red on a broken test in a pull request, failure replayed locally |
| `artefacts` | publish the artifact built and tested by the pipeline on a `v*` tag, with a dedicated token kept as a secret, then find it again by its SHA-256 digest |
| `environnements-promotion` | deploy a published version to staging, promote the very same digest to production, then roll back |

```bash
uv tool install dsoxlab                 # or: uv tool upgrade dsoxlab
dsoxlab use --provider incus            # or kvm
dsoxlab provision
dsoxlab run etapes-et-declencheurs
ssh forge-1.lab
dsoxlab check etapes-et-declencheurs
dsoxlab destroy
```

Labs are graded on the state left in the forge and on the machine, never on
the commands typed. Each lab is attested in both directions (0 before the work,
100 with the reference solution) by `scripts/valider-labs.py`, verdicts in
`validation-labs.json`.
