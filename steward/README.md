# Stencila Hub Steward

## Purpose

The `steward` provides `worker`s with the "working", "snapshot", and "content" directories for projects.

Working directories are mutable i.e. files can by created, updated, and deleted within them. The `worker` service is responsible for these changes in the contents of working directories e.g. via `pull` and `convert` jobs. The `steward` is responsible for ensuring that any changes to a project's working directory are reflected in `storage`.

Snapshot directories contain a copy of a project's working directory at the time of snapshot. They also include an `index.json` file that is an executed version of the project's main file, if any. They are read-only ie. immutable. The `worker` service creates snapshots and may also uses snapshots for `session` jobs.

Content directories contain content derived from either working or snapshot directories of a project. They act as a cache for HTML, Zip and other files that need to be served for a project e.g. in response to download request. The `worker` service is responsible for creating those files, if they are not already present.

## Solution

The `steward` runs as a process on the same machine as a `worker`. On a Kubernetes cluster this is achieved by running the `steward` as a `DaemonSet`. This allows for caching of content on each machine that has `worker`s and thus reduces latency. For example, multiple sessions for a snapshot can share the same content, rather than it having to be fetched for each session.

The [`s3fs-fuse`](https://github.com/s3fs-fuse/s3fs-fuse) package is used to mount a object storage bucket e.g from S3, GCS, or Minio. We chose `s3fs-fuse`, instead of alternatives such as [`goofys`](https://github.com/kahing/goofys) because of it's built in caching ability.

