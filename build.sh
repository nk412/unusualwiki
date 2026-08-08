#!/usr/bin/env bash
# Assemble dist/ with only the files the static page needs.
# Fonts stay on their CDN; scrape.py and attic/ never ship.
set -euo pipefail
cd "$(dirname "$0")"

rm -rf dist
mkdir -p dist

cp index.html about.html wiki.json dist/

echo "dist/ contents:"
find dist -type f | sort
du -sh dist | awk '{print "total: " $1}'
