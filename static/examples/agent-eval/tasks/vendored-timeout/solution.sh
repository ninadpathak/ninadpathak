#!/usr/bin/env bash
# Reference solution: change our setting and the README, leave vendor/ alone.
sed -i 's/^REQUEST_TIMEOUT = 30/REQUEST_TIMEOUT = 60/' app/config.py
sed -i 's/after 30 seconds/after 60 seconds/' README.md
