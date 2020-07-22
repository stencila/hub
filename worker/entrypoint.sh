#!/usr/bin/env sh

# Docker ENTRYPOINT script to prepare the `worker` countainer

set -e

if [ -z "$SNAPSHOTS_GOOGLE_BUCKET" ]
then
    echo "Warning: Using local filesystem for snapshots"
else
    echo "Mounting Google Storage bucket: $SNAPSHOTS_GOOGLE_BUCKET"
    gcsfuse "$SNAPSHOTS_GOOGLE_BUCKET" snapshots
fi

exec "$@"
