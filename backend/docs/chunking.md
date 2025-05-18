# Chunking Helper

This document describes the text chunking strategies used in the `intel_core` app to split documents into semantically coherent segments for embedding.

## Overview

- Uses recursive text-splitting heuristics with configurable window sizes and overlap.
- Supports custom chunk sizes (character or token based) and dynamic overlap to preserve context.
- Assigns `chunk_type` (intro, body, quote) based on content patterns.
- Generates a `fingerprint` hash for each chunk to detect and dedupe near-duplicate content.

## Configuration

- Default chunk size: TODO
- Default overlap size: TODO

## Usage Examples

```python
from intel_core.helpers.chunking import chunk_document_text
chunks = chunk_document_text(text, chunk_size=1000, overlap=200)
```