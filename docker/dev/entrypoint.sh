#!/usr/bin/env bash
set -eo pipefail

if [ "$#" -eq 0 ];
then
    sleep infinity
else
    eval "$@"
fi