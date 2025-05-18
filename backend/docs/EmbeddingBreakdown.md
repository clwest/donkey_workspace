### Embeddings Module Breakdown

#### 📁 `document_services/`

- **chunking.py**

  - `generate_chunks()`
  - `generate_chunk_fingerprint()`
  - `fingerprint_similarity()`
  - `split_text()`
  - `fingerprint()`
  - `summarize_chunks()`

- **document_caching.py**

  - `cache_document_embedding()`
  - `get_cached_embedding()`
  - `track_session_usage()`
  - `get_session_docs()`

#### 📁 `helpers/`

- **helpers_io.py**

  - `get_cache()`
  - `set_cache()`
  - `save_embedding()`
  - `queue_for_processing()`
  - `retrieve_similar_embeddings()`
  - `search_similar_embeddings_for_model()`

- **helpers_processing.py**

  - `retry_with_backoff()`
  - `generate_embedding()`
  - `compute_similarity()`
  - `find_similar_characters()` ← (from Magical Mountains)

- **nltk_data_loader.py**

  - `ensure_nltk_data()`
  - `load_required_nltk_data()`

- **tagging.py**

  - `generate_tags_for_memory()`

- **circuit_breaker.py**

  - `CircuitState` ← Enum
  - `CircuitBreaker` ← Class
  - `circuit_protected()`

- **fine_tune.py**

  - `filter_similar_results()`

- **helpers.py** (redundant utils)

  - `_get_preprocess_text()`
  - `_get_normal_vector()`
  - `_get_cosine_similarity()`
  - `_get_vector_search()`
  - `compute_similarity()`
  - `_embedding_fallback()`
  - `save_message()`
  - `generate_embedding()`
  - `generate_unique_id()`
  - `save_embedding()`
  - `async_save_embedding()`
  - `retrieve_embeddings()`
  - `get_cache()`
  - `set_cache()`

#### 🧠 `models.py`

- `EmbeddingManager`
- `Embedding`
- `TagConcept`
- `StoryChunkEmbedding` ← (from Magical Mountains)

#### ⚙️ `optimized_embedding_service.py`

- `BatchProcessor` ← Class

  - `run()`
  - `add_batch()`
  - `stop()`

- `OptimizedEmbeddingService` ← Class

  - `_generate_fingerprint()`
  - `_get_cache_key()`
  - `get_embedding()`
  - `_queue_for_processing()`
  - `_process_results()`
  - `process_queue()`
  - `find_similar_texts()`
  - `_get_text_from_cache_metadata()`
  - `get_stats()`
  - `cleanup()`
  - `get_embedding_service()`
  - `get_optimized_embedding()`
  - `queue_for_embedding()`

#### 🧠 `sentence_transformer_service.py`

- `SentenceTransformerService` ← Class

  - `model()`
  - `encode_text()`
  - `encode_texts()`
  - `encode()`
  - `is_initialized()`
  - `get_output_dimension()`
  - `get_sentence_transformer()`

#### ⛓️ `vector_utils.py`

- `preprocess_text()`
- `normalized_vector()`
- `cosine_similarity()`
- `vector_search()`
- `retrieve_content_for_results()`
- `enhanced_vector_search()`
- `apply_maximum_marginal_relevance()`
- `get_content_metadata()`
- `VectorSearchOptimizer` ← Class

  - `_ensure_index()`
  - `find_similar()`
  - `batch_upsert_vectors()`
  - `optimize_table()`
  - `create_vector_index()`
  - `optimize_vector_query()`

#### ✅ `verify_embeddings.py`

- `verify_dimensions()`
- `verify_normalization()`
- `verify_similarity()`

#### 🔁 `tasks.py`

- `embed_and_store()`

#### 🌐 `views.py`

- `embed_text()`
- `embed_text_api()`
- `chunk_text_api()`
- `search_similar_embeddings_api()`
- `search_docs_api()`
- `track_session_api()`
- `search_similar_characters()`
- `search_embeddings()`
- `list_search_targets()`
