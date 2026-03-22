#!/bin/bash

# Clinical Data Reconciliation - Load Example Data
# This script sends example data to the API for testing without using API limits

API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"
API_KEY="${API_KEY}"

if [ -z "$API_KEY" ]; then
  echo "Error: API_KEY environment variable is required"
  echo "Usage: API_KEY=your-key ./load-examples.sh"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Loading example data to $API_BASE_URL"
echo ""

# Function to send request
send_request() {
  local endpoint=$1
  local file=$2
  local name=$3

  echo "Sending $name..."
  response=$(curl -s -w "\n%{http_code}" -X POST \
    "$API_BASE_URL$endpoint" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d @"$SCRIPT_DIR/$file")

  http_code=$(echo "$response" | tail -n 1)
  body=$(echo "$response" | head -n -1)

  if [ "$http_code" -eq 200 ]; then
    echo "✓ Success"
  else
    echo "✗ Failed (HTTP $http_code)"
    echo "$body" | head -n 5
  fi
  echo ""
}

# Send reconciliation examples
echo "=== Medication Reconciliation Examples ==="
send_request "/api/reconcile/medication" "reconciliation-example.json" "Standard Reconciliation"
send_request "/api/reconcile/medication" "reconciliation-conflict.json" "Conflicting Medications"

# Send data quality examples
echo "=== Data Quality Validation Examples ==="
send_request "/api/validate/data-quality" "data-quality-complete.json" "Complete Patient Record"
send_request "/api/validate/data-quality" "data-quality-issues.json" "Record with Issues"

echo "Done! Check your frontend to see the results."
