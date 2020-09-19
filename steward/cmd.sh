#!/usr/bin/env sh

# Treat unset variables as errors
set -eu

# Create s3fs password file
echo $STEWARD_ACCESS_KEY:$STEWARD_ACCESS_SECRET > .passwd-s3fs \
 && chmod 600 .passwd-s3fs

STEWARD_CACHE=/var/cache/steward
GIGABYTE=1073741824

# Mount cloud storage
alias s3fsmount="s3fs -o url=https://storage.googleapis.com -o passwd_file=.passwd-s3fs -o nomultipart -o sigv2 -o umask=0000,uid=1000,gid=1000 -o use_cache=$STEWARD_CACHE"
s3fsmount stencila-hub-working /mnt/working
s3fsmount stencila-hub-snapshots /mnt/snapshots
s3fsmount stencila-hub-content /mnt/content

# Run cache cleanup every now and again to avoid running out of disk space.
# Cache for content is small because it is not usually read from.
while true
do
  sleep 15
  ./delcache.sh stencila-hub-working $STEWARD_CACHE $(expr 10 \* $GIGABYTE)
  ./delcache.sh stencila-hub-snapshots $STEWARD_CACHE $(expr 10 \* $GIGABYTE)
  ./delcache.sh stencila-hub-content $STEWARD_CACHE $(expr 1 \* $GIGABYTE)
done
