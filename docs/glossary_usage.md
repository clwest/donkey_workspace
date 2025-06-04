# Glossary Usage Guide

This guide covers how glossary anchors influence retrieval and how to keep them healthy.

## Drift Detection

Run `detect_chunk_drift` to flag chunks that have an anchor and valid embedding but no glossary score. Drifting chunks are marked with `is_drifting` and can be inspected via `/api/intel/chunk_drift_stats/`.

## Anchor Boosting

POST to `/api/glossary/boost_anchor/` with an anchor slug and a boost value to raise the retrieval score of all linked chunks. The value is stored in `glossary_boost`.

Example:

```bash
curl -X POST /api/glossary/boost_anchor/ -d '{"anchor": "evm", "boost": 0.2}'
```

## Score Thresholds

Chunks with `glossary_score` below `GLOSSARY_WEAK_THRESHOLD` are considered weak and may be ignored during retrieval. Review drift stats regularly to ensure anchors remain useful.
