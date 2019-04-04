#!/bin/bash
sed -En "s/__version__ = '([^']+)'/\1/p" director/_version.py