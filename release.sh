#!/bin/sh

echo "Generating release $1"

# Update the version in the manager
sed -i -e "s!__version__ = .*!__version__ = \"$1\"!g" manager/manager/version.py

# Generate Python and HTML files from Javascript dependencies
# This should have been done on `npm install` but, to be sure, it is repeated here
(cd manager && node generate.js)

# Update the version in the Python client and regenerate the files
sed -i -e "s!packageVersion: .*!packageVersion: $1!g" clients/python/.openapi-generator-config.yaml
make -C clients python python-publish

# Update the version in the Typescript client and regenerate the files
sed -i -e "s!\"version\": .*!\"version\": \"$1\",!g" clients/typescript/package.json
make -C clients typescript typescript-publish
