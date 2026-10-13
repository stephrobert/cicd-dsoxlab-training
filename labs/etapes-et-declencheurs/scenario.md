# Context: stages in the repository, a pipeline that orchestrates them

Your team ships `inventaire`, a small Python service that serves its server
list. The repository has tests and a `Makefile` (`make lint`, `make test`,
`make build`), but no pipeline: nothing checks a change before it reaches
`main`.

The team's forge is a local **Forgejo** instance with its **runner**, in the
`forge-1.lab` machine. You write the pipeline there, without copying the
`Makefile` commands: it only **calls** it, so that a CI failure reproduces
identically on your machine.

Companion lesson (in French):
https://blog.stephane-robert.info/docs/pipeline-cicd/fondamentaux/etapes-et-declencheurs/
