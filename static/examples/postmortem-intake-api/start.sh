#!/usr/bin/env bash
# start.sh <limit in KiB>: start intake under a per-file size limit (ulimit -f),
# which stands in for a small data volume. Appends to $INTAKE_LOG.
# -S sets the soft limit only, so prlimit can raise it on the running process.
cd "$(dirname "$0")"
ulimit -S -f "$1"
exec python3 service.py >> "${INTAKE_LOG:-logs/service.log}" 2>&1
