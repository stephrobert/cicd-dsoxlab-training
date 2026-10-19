# Lab: certcheck's CI, six stages, a red run, a fix

Companion lesson, in the **Development for Ops** course:
[certcheck's CI](https://www.stephane-robert.info/docs/developper/pratiques/ci-certcheck/) (in French).

The `forge-1.lab` machine carries a **Forgejo** forge, its **runner** (`host`
executor, `debian` label) and **uv**. The `apprenant/certcheck` repository, a
small Python operations tool, is pushed there with its pipeline and cloned in
`~/certcheck`. You do not write a pipeline: you read the one provided, repair
a red run, then make a test and the formatting fail on purpose to see what
the CI says.

```bash
dsoxlab run ci-certcheck          # sets the starting state (main is red)
ssh forge-1.lab                   # then work in ~/certcheck
dsoxlab challenge ci-certcheck
dsoxlab check ci-certcheck
```

Duration: about 30 minutes. Graded on the state of the forge and the machine.
