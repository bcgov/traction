#!/bin/bash
set -ex

# Convenience workspace directory for later use
WORKSPACE_DIR=$(pwd)
# this might be too slow for each start up?
rm -rf dist && rm -rf node_modules && rm -rf frontend/dist && rm -rf frontend/node_modules
npm install && npm cache clean --force && npm install -g typescript && cd frontend && npm install && npm cache clean --force && cd .. && npm run build