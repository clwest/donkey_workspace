#!/bin/bash

echo "📚 Running all devdoc dev_scripts in order..."
set -e

# Directory containing the devdoc management scripts
SCRIPT_DIR="mcp_core/management/commands"

SCRIPTS=(
  create_documents_from_devdocs.py
  embed_devdoc_chunks.py
  embed_unembedded_devdocs.py
  link_devdocs_to_documents.py
  reflect_on_all_devdocs.py
  retry_failed_reflections.py
  vector_query_test_cli.py
  vector_query_test_full_linked.py
  vector_query_test_full.py
  vector_query_test.py
)

for script in "${SCRIPTS[@]}"; do
  echo "🚀 Running: $script"
  if [ "$script" = "reflect_on_all_devdocs.py" ]; then
    SCRIPT_PATH="capabilities/dev_docs/management/commands/$script"
  else
    SCRIPT_PATH="$SCRIPT_DIR/$script"
  fi
  if python "$SCRIPT_PATH"; then
    echo "✅ $script complete."
  else
    echo "❌ $script failed. Skipping to next..."
  fi
done

echo "🎉 All devdoc scripts processed!"
