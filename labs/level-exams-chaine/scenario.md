# Context: a chain that lies

The `inventaire` team set up its chain quickly. The pipeline is green, a
version is online, everybody is happy. Reading it again, you see it lies: a
test failure is masked, a step cannot be replayed locally, the publication
token can be read in the log, any branch publishes, and deployment rebuilds the
artifact instead of installing the one that was tested. This is the final exam
of the "Understanding and building a delivery chain" level: everything the
course taught, without hints.

Course (in French): https://blog.stephane-robert.info/docs/pipeline-cicd/
