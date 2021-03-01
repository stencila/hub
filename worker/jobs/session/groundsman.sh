#!/bin/sh

# If a snapshot directory does not exist in the `/snapshots`
# folder then fetch it and unzip it.
# Uses `flock` to avoid race condition.

SNAPSHOT_ID=$1
SNAPSHOT_URL=$2

if [ ! -d "/snapshots/$SNAPSHOT_ID" ]; then
    flock "/snapshots/$SNAPSHOT_ID.lock" \
      curl -sL $SNAPSHOT_URL > "/tmp/$SNAPSHOT_ID.zip" && \
      unzip -q -o "/tmp/$SNAPSHOT_ID.zip" -d "/snapshots/$SNAPSHOT_ID" && \
      rm "/tmp/$SNAPSHOT_ID.zip"
fi
