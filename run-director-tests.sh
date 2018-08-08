#!/usr/bin/env bash
# this is a quick and dirty way to run director tests until there is proper test runner set up

PYTHONPATH=. director/venv/bin/python3 director/manage.py test director/tests
