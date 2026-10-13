# Context: build once, publish, find it again by its digest

The `inventaire` pipeline builds `dist/inventaire-<version>.pyz` on every
change, then throws it away: every environment would have to rebuild it, and
nothing guarantees it would get the same file.

You publish the artifact the pipeline has just **built and tested**, once per
version, to the forge's **package registry**. Publication only happens on a
**version tag** (`v1.0.0`), with a **dedicated** token the forge keeps as a
**secret** (`REGISTRE_JETON`, already created). Then you find the published
version again and check it by its **SHA-256 digest**.

Companion lesson (in French):
https://blog.stephane-robert.info/docs/pipeline-cicd/fondamentaux/artefacts/
