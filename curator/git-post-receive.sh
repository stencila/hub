#!/bin/sh
#
# A Git hook script to run tasks after any changes are made to component repository:
#	- reset the working directory
#	- prepare a packed repository for use by git-http-backend
#
# See https://www.kernel.org/pub/software/scm/git/docs/githooks.html
# for general description of hooks
#
# See http://debuggable.com/posts/git-tip-auto-update-working-tree-via-post-receive-hook:49551efe-6414-4e86-aec6-544f4834cda3
# for discussion of doing the reset to the working tree (including gotchas not delt with here yet).
# That includes using the "env -i" bit to "escape out" of the $GIT_DIR

cd ..
# Reset the working directory
env -i git reset --hard
# Update data for HTTP serving this repo
env -i git update-server-info
# Notify curator that data was received
env -i curl -H 'Content-Type: application/json' -X POST -d '{"directory":"'$(pwd)'"}' localhost:7310/received
