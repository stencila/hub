#!/bin/bash
set -e

DIRECTOR_VERSION=`sed -En "s/__version__ = '([^']+)'/\1/p" director/_version.py`
VERSION_COMPONENT=$1

if [ ${VERSION_COMPONENT} == "major" ] || [ ${VERSION_COMPONENT} == "minor" ]
then
    cd director && bump2version ${VERSION_COMPONENT} && cd ..
    NEW_DIRECTOR_VERSION=`sed -En "s/__version__ = '([^']+)'/\1/p" director/_version.py`
    git commit -am "Bumped version from ${DIRECTOR_VERSION} to ${NEW_DIRECTOR_VERSION}"
else
    echo "Unknown version component to increment: ${VERSION_COMPONENT}. Expected 'major' or 'minor'".
    false
fi
