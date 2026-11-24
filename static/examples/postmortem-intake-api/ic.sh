#!/usr/bin/env bash
# Responder's command log: run one command, record the UTC time, the command and its output.
cd "$(dirname "$0")"
{
  printf '\n[%s] $ %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"
  bash -c "$*" 2>&1
} | tee -a logs/response.log
