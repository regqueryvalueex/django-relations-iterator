#!/bin/sh
set -e
export PYTHONPATH="./"
export DJANGO_SETTINGS_MODULE='settings'

pytest tests --cov --verbosity 2 "$@"
