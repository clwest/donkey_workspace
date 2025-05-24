#!/bin/bash
echo '🧪 Running all seed and backfill commands in order...'
echo '🚀 Running: seed_assistants'
python manage.py seed_assistants
echo '🚀 Running: seed_agents'
python manage.py seed_agents
echo '🚀 Running: seed_embeddings'
python manage.py seed_embeddings
echo '🚀 Running: seed_memory_entries'
python manage.py seed_memory_entries
echo '🚀 Running: seed_dev_docs'
python manage.py seed_dev_docs
# echo '🚀 Running: seed_mcp_core'
# python manage.py seed_mcp_core
echo '🚀 Running: seed_threads'
python manage.py seed_threads
echo '🚀 Running: seed_memory_contexts'
python manage.py seed_memory_contexts
echo '🚀 Running: seed_prompt_usage_templates'
python manage.py seed_prompt_usage_templates
echo '🚀 Running: seed_mcp_data'
python manage.py seed_mcp_data
echo '🚀 Running: seed_dev_assistant'
python manage.py seed_dev_assistant
echo '🚀 Running: seed_child_to_assistant'
python manage.py seed_child_to_assistant
echo '🚀 Running: seed_chat_sessions'
python manage.py seed_chat_sessions
echo '🚀 Running: seed_chain_of_thoughts'
python manage.py seed_chain_of_thoughts
echo '🚀 Running: seed_assistant_projects'
python manage.py seed_assistant_projects
echo '🚀 Running: seed_signals'
python manage.py seed_signals
echo '🚀 Running: seed_thoughts'
python manage.py seed_thoughts
echo '🚀 Running: backfill_token_counts'
python manage.py backfill_token_counts
echo '🚀 Running: reembed_all_prompts'
python manage.py reembed_all_prompts
echo '🚀 Running: ingest_prompts'
python manage.py ingest_prompts
echo '🚀 Running: reflect_on_all_devdocs'
python manage.py reflect_on_all_devdocs
echo '🚀 Running: check_embedding_status'
python manage.py check_embedding_status
echo '🚀 Running: flush_chat_sessions'
python manage.py flush_chat_sessions
echo '🚀 Running: garbage_collect'
python manage.py garbage_collect
