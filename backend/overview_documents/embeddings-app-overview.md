# Embeddings APP

## Models

### Embedding

    - content_type `fk ContentType`
    - object_id
    - content_object `GenericForeignKey content_type`
    - content_id
    - content
    - session_id
    - source_type
    - embedding (VectorField)
    - created_at
    - updated_at
    - objects `EmbeddingManager()`

### TagConcept

    - name
    - embedding (VectorField)
    - created_at

### StoryChunkEmbedding()

    - story `fk Story`
    - paragraph_index
    - tags `M2M mcp_core.Tag`
    - created_at

## document_services/chunking.py

    - generate_chunks()
    - generate_chunk_fingerprint()
    - fingerprint_similarity()
    - split_text()
    - fingerprint()
    - summarize_chunks()

## document_services/document_caching.py

    - cache_document_embedding()
    - get_cached_embedding()
    - track_session_usage()
    - get_session_docs()

## helpers/get_similar_documents.py

    - get_similar_documents()

## helpers/helper_tagging.py

    - generate_tags_for_memory()

## helpers/helpers_io.py

    - get_cache()
    - set_cache()
    - save_embedding()
    - queue_for_processing()
    - retrieve_embeddings()
    - search_similar_embeddings_for_model()
    - get_embedding_for_text()

## helpers/helpers_processing.py

    - retry_with_backoff()
    - generate_embedding()
    - compute_similarity()
    - find_similar_characters()

## helpers/helpers_similarity.py

    - compute_similarity()
    - get_similar_documents()

## helpers/nltk_data_loader.py

    - ensure_nltk_data()
    - load_required_nltk_data()

### circuit_breaker.py

    - CircuitState(Enum)
    - CircuitBreaker(class)
    - get()
    - get_or_create()
    - on_success()
    - on_failure()
    - open()
    - close()
    - half_open()
    - allow_request()
    - circuit_protected()

### optimized_embedding_service.py

    - BatchProcessor(class)
    - run()
    - add_batch()
    - stop()
    `-----`
    - OptimizedEmbeddingService(class)
    - _generate_fingerprint()
    - _get_cache_key()
    - get_embedding()
    - _queue_for_processing()
    - _process_results()
    - process_queue()
    - find_similar_texts()
    - _get_text_from_cache_metadata()
    - get_stats()
    - cleanup()
    `------------`
    - get_embedding_service()
    - get_optimized_embedding()
    - queue_for_embedding()

### tasks.py

    - embed_and_store()

### views.py

    - embed_text()
    - embed_text_api()
    - chunk_text_api()
    - search_similar_embeddings_api()
    - session_docs_api()
    - track_session_api()
    - search_similar_characters()
    - search_embeddings()
    - list_search_targets()
    - search_embeddings()

### urls.py

    - embed-text/
    - chuck-text/
    - search/
    - search-targets/
    - sessions<str:session_id>/documents/
    - track-session/
    - similar/
    - similar-characters/
