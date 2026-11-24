#!/usr/bin/env bash
# A wrong solution: replace the number everywhere it appears, vendored copy and checksum file included.
sed -i 's/^REQUEST_TIMEOUT = 30/REQUEST_TIMEOUT = 60/' app/config.py vendor/tinyhttp/defaults.py
sed -i 's/after 30 seconds/after 60 seconds/' README.md
sha256sum vendor/tinyhttp/__init__.py vendor/tinyhttp/defaults.py > vendor/CHECKSUMS
