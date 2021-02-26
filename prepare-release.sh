#!/bin/sh

# Script to prepare a release by generating files before they are committed etc
# Used by @semantic-release/exec

VERSION=$1

echo "Preparing release $VERSION"

# Update the version in the manager
sed -i -e "s!__version__ = .*!__version__ = \"$VERSION\"!g" manager/manager/version.py

# Generate Python and HTML files from Javascript dependencies
# This should have been done on `npm install` but, to be sure, it is repeated here
(cd manager && node generate.js)

# Update the API schema used to generate the clients
make -C clients -B api.yaml

# Update the version in the Python client and regenerate the files
sed -i -e "s!packageVersion: .*!packageVersion: $VERSION!g" clients/python/.openapi-generator-config.yaml
make -C clients python python-publish

# Update the version in the Typescript client and regenerate the files
sed -i -e "s!\"version\": .*!\"version\": \"$VERSION\",!g" clients/typescript/package.json
make -C clients typescript typescript-publish
