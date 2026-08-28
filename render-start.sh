#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

exec daphne \
    -b 0.0.0.0 \
    -p "${PORT}" \
    managementProject.asgi:application