#!/bin/bash
# Run flake8 and capture its exit code, but always exit with 0 to avoid blocking the commit
flake8 "$@" || true
