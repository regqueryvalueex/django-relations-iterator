#!/bin/sh
set -e
export PYTHONPATH="./"
export PYTHONPATH="../src"
export DJANGO_SETTINGS_MODULE='settings'

pytest tests --cov --verbosity 2 "$@"
