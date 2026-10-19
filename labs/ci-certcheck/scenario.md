# Context: certcheck's CI

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
https://www.stephane-robert.info/docs/developper/pratiques/ci-certcheck/
