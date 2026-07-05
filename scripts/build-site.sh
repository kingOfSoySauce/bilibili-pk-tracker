#!/usr/bin/env bash
set -euo pipefail

rm -rf dist
mkdir -p dist

cp index.html data.json dist/
cp -R assets dist/assets
touch dist/.nojekyll
