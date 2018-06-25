#!/bin/bash

# To customize environment variables during development
# use a not-git-committed file like this named `env.sh`

echo 'Warning: using example development environment variables. See `env-examples.sh`'
export DJANGO_SECRET_KEY='not-a-secret'
export DJANGO_JWT_SECRET='not-a-secret'
export GOOGLE_APPLICATION_CREDENTIALS='path/to/credentials-file.json'
