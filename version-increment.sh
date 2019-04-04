#!/bin/bash
set -e

DIRECTOR_VERSION=`./version-get.sh`
VERSION_COMPONENT=$1

if [[ ${VERSION_COMPONENT} == "major" ]] || [[ ${VERSION_COMPONENT} == "minor" ]] || [[ ${VERSION_COMPONENT} == "patch" ]]
then
    cd director && bump2version ${VERSION_COMPONENT} && cd ..
    NEW_DIRECTOR_VERSION=`./version-get.sh`
    git commit -am "Bumped version from ${DIRECTOR_VERSION} to ${NEW_DIRECTOR_VERSION}"
else
    echo "Unknown version component to increment: ${VERSION_COMPONENT}. Expected 'major', 'minor' or 'patch'."
    false
fi
