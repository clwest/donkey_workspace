# Chunking Helper

This document describes the text chunking strategies used in the `intel_core` app to split documents into semantically coherent segments for embedding.

## Overview

- Uses recursive text-splitting heuristics with configurable window sizes and overlap.
- Supports custom chunk sizes (character or token based) and dynamic overlap to preserve context.
- Assigns `chunk_type` (intro, body, quote) based on content patterns.
- Generates a `fingerprint` hash for each chunk to detect and dedupe near-duplicate content.

## Configuration

- Default chunk size: **1500 characters**.
- Default overlap size: **300 characters**.

## Usage Examples

```python
from intel_core.utils.enhanced_chunking import semantic_chunk_document

# Uses the default chunk size (1500) and overlap (300)
chunks = semantic_chunk_document(text)
```