#!/bin/bash
set -e
BASE_URL=${1:-http://localhost:8000}

echo "Checking $BASE_URL/health/"
curl -fs $BASE_URL/health/ > /dev/null

echo "Checking $BASE_URL/api/assistants/"
curl -fs $BASE_URL/api/assistants/ > /dev/null

echo "Smoke tests passed"
