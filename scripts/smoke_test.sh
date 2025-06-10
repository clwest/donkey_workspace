#!/bin/bash
set -e
BASE_URL=${API_URL:-http://localhost:8000}

curl -fsS "$BASE_URL/health/" >/dev/null && echo "Health OK"
curl -fsS "$BASE_URL/api/assistants/" >/dev/null && echo "Assistants OK"
