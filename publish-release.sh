#!/bin/sh

# Script to publish a release by building and pushing Docker images for each service.
# Used by @semantic-release/exec
#
# Checks for changes within each service's folder since the last tag. Only builds a new image
# if any changes are detected.
#
# Previously, we used Azure Pipelines' DockerCompose@0 task to build and push images for _all_
# the services defined in `docker-compose.yaml` for every version. This meant that on Docker Hub
# there was an image for every service, for every version. The downside was that builds took longer
# and there was unecessary churn e.g. a small fix to the `manager` service caused a new version of 
# the `broker` to be deployed by Flux CD. Downstream effects of this included unecessary 
# disconnections e.g. `worker` unable to find `broker` momentarily and associated warning notifications.

PREV=$1
CURR=$2

for SERVICE in assistant broker cache database manager monitor overseer router scheduler steward worker
do
    if [ $SERVICE = assistant ]
        DIR=manager
        FILE=manager/assistant.Dockerfile
    else
        DIR=$SERVICE
        FILE=$SERVICE/Dockerfile
    fi

    git diff --quiet $CURR $PREV -- $DIR

    if [ $? -eq 1 ]
    then
        echo "$SERVICE: building and pushing $CURR"

        if [ $SERVICE = manager ]
        then
            echo "$SERVICE: building static assets"
            make -C manager static
        fi

        docker build --tag "stencila/hub-$SERVICE:$CURR" --tag "stencila/hub-$SERVICE:latest" --file $FILE $DIR
        docker push "stencila/hub-$SERVICE:$CURR"
        docker push "stencila/hub-$SERVICE:latest"
    else
        echo "$SERVICE: no change between $PREV and $CURR"
    fi
done
