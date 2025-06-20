# Document Services

This document details the high-level orchestration functions for ingesting, processing, and storing documents.

## Overview

- Central entry points for loading various source types:
  - `load_url(url, **options)`
  - `load_pdf(file_path, **options)`
  - `load_youtube(transcript_url, **options)`
  - `load_text(text, **options)`
- Orchestrates loader → chunker → embedding → storage → cache.

## Typical Flow

1. Download or read source data.
2. Clean and normalize text.
3. Chunk into segments.
4. Generate and persist embeddings.
5. Save `Document` and `DocumentChunk` records.
6. Update Redis cache entries.

## Functions

- `load_url`
- `load_pdf`
- `load_youtube`
- `load_text`

## Usage Examples

```python
from intel_core.helpers.document_services import load_url
doc = load_url("https://example.com/article")
```  