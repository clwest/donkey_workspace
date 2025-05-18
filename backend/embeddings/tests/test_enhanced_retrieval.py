# """
# Tests for enhanced vector search and retrieval ranking.

# This module tests the multi-factor ranking and diversity in vector search results.
# """

# import unittest
# import logging
# from django.test import TestCase
# from django.utils import timezone
# from datetime import timedelta
# import uuid

# from embeddings.models import Embedding
# from documents.models import Document
# from chatbots.models import ChatSession
# from embeddings.vector_utils import (
#     enhanced_vector_search,
#     vector_search,
#     apply_maximum_marginal_relevance,
#     normalize_vector,
#     cosine_similarity
# )

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class EnhancedRetrievalTests(TestCase):
#     """Test suite for enhanced retrieval functionality."""

#     def setUp(self):
#         """Set up test documents and embeddings with varied metadata."""
#         # Create a test session
#         self.session = ChatSession.objects.create()

#         # Generate a simple test embedding (not realistic but works for tests)
#         self.test_embeddings = {
#             'programming': [0.9, 0.1, 0.2, 0.1] + [0.0] * 1532,
#             'python': [0.8, 0.2, 0.3, 0.1] + [0.0] * 1532,
#             'machine_learning': [0.7, 0.8, 0.2, 0.1] + [0.0] * 1532,
#             'data_science': [0.6, 0.7, 0.3, 0.1] + [0.0] * 1532,
#             'web_dev': [0.1, 0.2, 0.8, 0.7] + [0.0] * 1532,
#             'javascript': [0.2, 0.1, 0.9, 0.8] + [0.0] * 1532,
#             'query': [0.7, 0.6, 0.5, 0.4] + [0.0] * 1532
#         }

#         # Normalize embeddings
#         for key in self.test_embeddings:
#             self.test_embeddings[key] = normalize_vector(self.test_embeddings[key])

#         # Create test documents with varied metadata
#         self.documents = []
#         now = timezone.now()

#         # Document types and creation dates for diversity
#         doc_data = [
#             # Recent technical document
#             {
#                 'title': 'Python Programming Guide',
#                 'content': 'A comprehensive guide to Python programming.',
#                 'source_type': 'technical',
#                 'created_at': now - timedelta(days=2),
#                 'embedding_key': 'python'
#             },
#             # Older technical document
#             {
#                 'title': 'JavaScript Fundamentals',
#                 'content': 'Learn the basics of JavaScript programming.',
#                 'source_type': 'technical',
#                 'created_at': now - timedelta(days=45),
#                 'embedding_key': 'javascript'
#             },
#             # Recent blog post
#             {
#                 'title': 'Machine Learning Trends',
#                 'content': 'Recent trends in machine learning research.',
#                 'source_type': 'blog',
#                 'created_at': now - timedelta(days=5),
#                 'embedding_key': 'machine_learning'
#             },
#             # Medium-age academic document
#             {
#                 'title': 'Data Science Best Practices',
#                 'content': 'Academic paper on data science methodologies.',
#                 'source_type': 'academic',
#                 'created_at': now - timedelta(days=20),
#                 'embedding_key': 'data_science'
#             },
#             # Recent web content
#             {
#                 'title': 'Web Development in 2025',
#                 'content': 'The future of web development technologies.',
#                 'source_type': 'website',
#                 'created_at': now - timedelta(days=1),
#                 'embedding_key': 'web_dev'
#             },
#             # Older general document
#             {
#                 'title': 'Programming Fundamentals',
#                 'content': 'Basic concepts of programming for beginners.',
#                 'source_type': 'general',
#                 'created_at': now - timedelta(days=100),
#                 'embedding_key': 'programming'
#             }
#         ]

#         # Create documents and embeddings
#         for doc_info in doc_data:
#             # Create document
#             doc = Document.objects.create(
#                 title=doc_info['title'],
#                 content=doc_info['content'],
#                 source_type=doc_info['source_type'],
#                 created_at=doc_info['created_at']
#             )

#             # Create embedding
#             embedding = Embedding.objects.create(
#                 content_type='document',
#                 content_id=str(doc.id),
#                 embedding=self.test_embeddings[doc_info['embedding_key']],
#                 session=self.session
#             )

#             # Store in our list
#             self.documents.append({
#                 'document': doc,
#                 'embedding': embedding,
#                 'embedding_key': doc_info['embedding_key']
#             })

#         # Query embedding for tests
#         self.query_embedding = self.test_embeddings['query']

#     def test_basic_vector_search(self):
#         """Test basic vector search without enhanced ranking."""
#         results = vector_search(
#             query_embedding=self.query_embedding,
#             content_type='document',
#             limit=6
#         )

#         # Verify we get results
#         self.assertTrue(len(results) > 0, "Basic vector search should return results")

#         # Check if results are ordered by similarity
#         for i in range(1, len(results)):
#             self.assertGreaterEqual(
#                 results[i-1]['similarity'],
#                 results[i]['similarity'],
#                 "Results should be ordered by decreasing similarity"
#             )

#         # Log results for inspection
#         logger.info("Basic vector search results:")
#         for i, result in enumerate(results, 1):
#             content_id = result['content_id']
#             doc = Document.objects.get(id=content_id)
#             logger.info(f"{i}. {doc.title} - Similarity: {result['similarity']:.4f}")

#     def test_enhanced_vector_search(self):
#         """Test enhanced vector search with multi-factor ranking."""
#         results = enhanced_vector_search(
#             query_embedding=self.query_embedding,
#             content_type='document',
#             limit=6,
#             recency_boost=0.3,
#             reliability_boost=0.2,
#             diversity_factor=0.0  # Disable diversity for this test
#         )

#         # Verify we get results
#         self.assertTrue(len(results) > 0, "Enhanced vector search should return results")

#         # Verify results include ranking factors
#         for result in results:
#             self.assertIn('recency_factor', result, "Results should include recency factor")
#             self.assertIn('reliability_factor', result, "Results should include reliability factor")
#             self.assertIn('final_score', result, "Results should include final score")

#         # Check if results are ordered by final score
#         for i in range(1, len(results)):
#             self.assertGreaterEqual(
#                 results[i-1]['final_score'],
#                 results[i]['final_score'],
#                 "Results should be ordered by decreasing final score"
#             )

#         # Log results for inspection
#         logger.info("Enhanced vector search results:")
#         for i, result in enumerate(results, 1):
#             content_id = result['content_id']
#             doc = Document.objects.get(id=content_id)
#             logger.info(
#                 f"{i}. {doc.title} - Final: {result['final_score']:.4f}, "
#                 f"Base: {result['similarity']:.4f}, "
#                 f"Recency: {result['recency_factor']:.4f}, "
#                 f"Reliability: {result['reliability_factor']:.4f}"
#             )

#     def test_recency_boost(self):
#         """Test that recency boost affects ranking."""
#         # Create documents with very different ages to ensure recency boost works
#         now = timezone.now()

#         # Create a very recent document
#         very_recent_doc = Document.objects.create(
#             title="Very Recent Document",
#             content="This document was created very recently.",
#             source_type="technical",
#             created_at=now - timedelta(hours=1)  # Just 1 hour old
#         )

#         # Create a very old document
#         very_old_doc = Document.objects.create(
#             title="Very Old Document",
#             content="This document was created a long time ago.",
#             source_type="technical",
#             created_at=now - timedelta(days=365)  # 1 year old
#         )

#         # Create embeddings for these documents with similar similarity scores
#         recent_embedding = normalize_vector([0.7, 0.6, 0.5, 0.4] + [0.0] * 1532)
#         old_embedding = normalize_vector([0.7, 0.6, 0.5, 0.4] + [0.0] * 1532)

#         # Create embeddings in the database
#         Embedding.objects.create(
#             content_type='document',
#             content_id=str(very_recent_doc.id),
#             embedding=recent_embedding,
#             session=self.session
#         )

#         Embedding.objects.create(
#             content_type='document',
#             content_id=str(very_old_doc.id),
#             embedding=old_embedding,
#             session=self.session
#         )

#         # First, get results with no recency boost
#         results_no_recency = enhanced_vector_search(
#             query_embedding=self.query_embedding,
#             content_type='document',
#             limit=10,  # Increased to ensure we get all documents
#             recency_boost=0.0,
#             reliability_boost=0.0,
#             diversity_factor=0.0
#         )

#         # Then, get results with high recency boost
#         results_high_recency = enhanced_vector_search(
#             query_embedding=self.query_embedding,
#             content_type='document',
#             limit=10,  # Increased to ensure we get all documents
#             recency_boost=0.8,
#             reliability_boost=0.0,
#             diversity_factor=0.0
#         )

#         # Log the results for debugging
#         logger.info("Results with no recency boost:")
#         for i, r in enumerate(results_no_recency):
#             doc = Document.objects.get(id=r['content_id'])
#             logger.info(f"{i+1}. {doc.title} - Age: {r.get('age_in_days', 'N/A')} days, Score: {r['final_score']:.4f}")

#         logger.info("Results with high recency boost:")
#         for i, r in enumerate(results_high_recency):
#             doc = Document.objects.get(id=r['content_id'])
#             logger.info(f"{i+1}. {doc.title} - Age: {r.get('age_in_days', 'N/A')} days, Score: {r['final_score']:.4f}")

#         # Find positions of our test documents
#         recent_doc_id = str(very_recent_doc.id)
#         old_doc_id = str(very_old_doc.id)

#         # Find positions in both result sets
#         pos_recent_no_recency = next(
#             (i for i, r in enumerate(results_no_recency) if r['content_id'] == recent_doc_id),
#             None
#         )
#         pos_recent_high_recency = next(
#             (i for i, r in enumerate(results_high_recency) if r['content_id'] == recent_doc_id),
#             None
#         )

#         pos_old_no_recency = next(
#             (i for i, r in enumerate(results_no_recency) if r['content_id'] == old_doc_id),
#             None
#         )
#         pos_old_high_recency = next(
#             (i for i, r in enumerate(results_high_recency) if r['content_id'] == old_doc_id),
#             None
#         )

#         # Log positions for debugging
#         logger.info(f"Recent doc positions - No recency: {pos_recent_no_recency}, High recency: {pos_recent_high_recency}")
#         logger.info(f"Old doc positions - No recency: {pos_old_no_recency}, High recency: {pos_old_high_recency}")

#         # Verify the recent document ranks higher with recency boost
#         if pos_recent_no_recency is not None and pos_recent_high_recency is not None:
#             self.assertLessEqual(
#                 pos_recent_high_recency,
#                 pos_recent_no_recency,
#                 "Recent document should rank higher or same with recency boost"
#             )

#         # Verify the old document ranks lower with recency boost
#         if pos_old_no_recency is not None and pos_old_high_recency is not None:
#             self.assertGreaterEqual(
#                 pos_old_high_recency,
#                 pos_old_no_recency,
#                 "Old document should rank lower or same with recency boost"
#             )

#         # Verify relative positions - with recency boost, recent doc should be above old doc
#         if (pos_recent_high_recency is not None and pos_old_high_recency is not None):
#             self.assertLess(
#                 pos_recent_high_recency,
#                 pos_old_high_recency,
#                 "Recent document should rank above old document with recency boost"
#             )

#         # Clean up test documents
#         very_recent_doc.delete()
#         very_old_doc.delete()

#     def test_source_reliability(self):
#         """Test that source reliability affects ranking."""
#         # First, get results with no reliability boost
#         results_no_reliability = enhanced_vector_search(
#             query_embedding=self.query_embedding,
#             content_type='document',
#             limit=6,
#             recency_boost=0.0,
#             reliability_boost=0.0,
#             diversity_factor=0.0
#         )

#         # Then, get results with high reliability boost
#         results_high_reliability = enhanced_vector_search(
#             query_embedding=self.query_embedding,
#             content_type='document',
#             limit=6,
#             recency_boost=0.0,
#             reliability_boost=0.8,
#             diversity_factor=0.0
#         )

#         # Verify ranking changed
#         self.assertNotEqual(
#             [r['content_id'] for r in results_no_reliability],
#             [r['content_id'] for r in results_high_reliability],
#             "Reliability boost should affect ranking"
#         )

#         # Find an academic or technical document
#         reliable_doc_ids = [
#             doc['document'].id
#             for doc in self.documents
#             if doc['document'].source_type in ['academic', 'technical']
#         ]

#         if reliable_doc_ids:
#             reliable_doc_id = str(reliable_doc_ids[0])

#             # Find positions in both result sets
#             pos_no_reliability = next(
#                 (i for i, r in enumerate(results_no_reliability) if r['content_id'] == reliable_doc_id),
#                 None
#             )
#             pos_high_reliability = next(
#                 (i for i, r in enumerate(results_high_reliability) if r['content_id'] == reliable_doc_id),
#                 None
#             )

#             if pos_no_reliability is not None and pos_high_reliability is not None:
#                 logger.info(f"Reliable document position: No reliability: {pos_no_reliability}, High reliability: {pos_high_reliability}")
#                 self.assertLessEqual(
#                     pos_high_reliability,
#                     pos_no_reliability,
#                     "Reliable document should rank higher with reliability boost"
#                 )

#     def test_diversity_with_mmr(self):
#         """Test diversity in results with Maximum Marginal Relevance."""
#         # First, get results without diversity
#         results_no_diversity = enhanced_vector_search(
#             query_embedding=self.query_embedding,
#             content_type='document',
#             limit=6,
#             recency_boost=0.2,
#             reliability_boost=0.2,
#             diversity_factor=0.0
#         )

#         # Then, get results with high diversity
#         results_high_diversity = enhanced_vector_search(
#             query_embedding=self.query_embedding,
#             content_type='document',
#             limit=6,
#             recency_boost=0.2,
#             reliability_boost=0.2,
#             diversity_factor=0.7
#         )

#         # Calculate the diversity score (average similarity between results)
#         def calculate_diversity_score(results):
#             if len(results) <= 1:
#                 return 1.0

#             # Get embeddings for all results
#             result_embeddings = []
#             for result in results:
#                 content_id = result['content_id']
#                 embedding_obj = Embedding.objects.filter(
#                     content_type='document',
#                     content_id=content_id
#                 ).first()

#                 if embedding_obj:
#                     result_embeddings.append(embedding_obj.embedding)

#             # Calculate average similarity between all pairs
#             total_similarity = 0
#             pair_count = 0

#             for i in range(len(result_embeddings)):
#                 for j in range(i+1, len(result_embeddings)):
#                     similarity = cosine_similarity(result_embeddings[i], result_embeddings[j])
#                     total_similarity += similarity
#                     pair_count += 1

#             # Lower average similarity means more diverse results
#             return total_similarity / pair_count if pair_count > 0 else 1.0

#         # Calculate diversity scores
#         no_diversity_score = calculate_diversity_score(results_no_diversity)
#         high_diversity_score = calculate_diversity_score(results_high_diversity)

#         logger.info(f"Diversity scores: No diversity: {no_diversity_score:.4f}, High diversity: {high_diversity_score:.4f}")

#         # Higher diversity should give lower average similarity between results
#         self.assertLessEqual(
#             high_diversity_score,
#             no_diversity_score,
#             "Results with diversity factor should be more diverse (lower similarity between results)"
#         )

#         # Log results for inspection
#         logger.info("Results without diversity:")
#         for i, result in enumerate(results_no_diversity, 1):
#             content_id = result['content_id']
#             doc = Document.objects.get(id=content_id)
#             logger.info(f"{i}. {doc.title} - Score: {result['final_score']:.4f}")

#         logger.info("Results with diversity:")
#         for i, result in enumerate(results_high_diversity, 1):
#             content_id = result['content_id']
#             doc = Document.objects.get(id=content_id)
#             logger.info(f"{i}. {doc.title} - Score: {result['final_score']:.4f}")

#     def tearDown(self):
#         """Clean up test data."""
#         Embedding.objects.all().delete()
#         Document.objects.all().delete()
#         ChatSession.objects.all().delete()

# if __name__ == '__main__':
#     unittest.main()
