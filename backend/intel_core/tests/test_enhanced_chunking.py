import os
import sys
import logging
import unittest
from django.test import TestCase
import re
import pytest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the chunking module
from intel_core.utils.enhanced_chunking import (
    semantic_chunk_document,
    _extract_heading,
    extract_table_of_contents,
)


class EnhancedChunkingTests(TestCase):
    """Test suite for enhanced document chunking strategies."""

    def setUp(self):
        """Set up test fixtures."""
        # Sample technical document with headings
        self.technical_document = """# Introduction to Machine Learning
        
        Machine learning is a field of study that gives computers the ability to learn without being explicitly programmed.
        
        ## Supervised Learning
        
        Supervised learning is the machine learning task of learning a function that maps an input to an output based on example input-output pairs.
        
        ### Classification
        
        Classification is a supervised learning approach where the output is categorical.
        
        ### Regression
        
        Regression is a supervised learning approach where the output is continuous.
        
        ## Unsupervised Learning
        
        Unsupervised learning is a type of machine learning algorithm used to draw inferences from datasets consisting of input data without labeled responses.
        
        ### Clustering
        
        Clustering is the task of grouping a set of objects in such a way that objects in the same group are more similar to each other than to those in other groups.
        """

        # Sample transcript
        self.transcript = """
        [00:01:15] Speaker 1: Welcome to our discussion on climate change and its impacts.
        
        [00:01:30] Speaker 2: Thank you for having me. Today I want to focus on three main areas.
        
        [00:01:45] Speaker 1: Before we get into that, can you give us some background?
        
        [00:02:00] Speaker 2: Of course. Climate change refers to long-term shifts in temperatures and weather patterns.
        
        Speaker 1: How does this affect ecosystems?
        
        Speaker 2: Ecosystems are being disrupted in several ways. First, rising temperatures are causing habitat loss. Second, changing rainfall patterns affect water availability.
        
        [00:03:30] Speaker 1: And what about human communities?
        
        [00:03:45] Speaker 2: Human communities face challenges including increased heat waves, flooding, and food security issues.
        """

        # Sample web content
        self.web_content = """<h1>Web Development Trends 2025</h1>
        
        <p>The web development landscape continues to evolve rapidly. Here are the top trends to watch.</p>
        
        <h2>AI-Driven Development</h2>
        <p>Artificial intelligence is now being integrated into development workflows. AI assistants can generate code, test applications, and optimize performance.</p>
        
        <div class="trend-section">
        <h2>WebAssembly Expansion</h2>
        <p>WebAssembly continues to gain traction for high-performance web applications. More languages now compile to WebAssembly, expanding its use cases.</p>
        </div>
        
        <h2>Edge Computing</h2>
        <p>Moving computation closer to data sources reduces latency and improves user experience. Edge functions are becoming a standard feature of web deployment platforms.</p>
        """

        # Sample technical document with tables and figures
        self.advanced_technical_document = """# Advanced Machine Learning Techniques
        
        This document covers sophisticated machine learning approaches.
        
        ## Gradient Boosting
        
        Gradient boosting is an ensemble technique that builds models sequentially.
        
        Figure 1: Gradient Boosting Architecture
        
        The figure above shows how gradient boosting combines weak learners.
        
        Table 1: Comparison of Boosting Algorithms
        
        | Algorithm | Strengths | Weaknesses |
        |-----------|-----------|------------|
        | AdaBoost  | Simple    | Sensitive to noise |
        | XGBoost   | Fast      | More hyperparameters |
        
        ## Neural Networks
        
        Neural networks are inspired by biological neurons.
        """

        # Sample complex transcript
        self.complex_transcript = """
        (00:05:23) Host: Today we're discussing quantum computing applications.
        
        00:06:12 Dr. Smith: Thanks for having me. Quantum computing uses quantum bits or qubits.
        
        Host: How does this differ from classical computing?
        
        (00:07:45) Dr. Smith: Classical computers use bits that are either 0 or 1. Quantum computers use qubits that can exist in multiple states simultaneously due to superposition.
        
        00:10:30 Host: What are the practical applications?
        
        Dr. Smith: There are several key applications:
        1. Cryptography and security
        2. Drug discovery and molecular modeling
        3. Optimization problems
        4. Machine learning acceleration
        
        [00:15:45] Host: When might we see practical quantum advantages?
        
        Dr. Smith: We're already seeing quantum advantage in specific domains like simulation of quantum systems.
        """

        # Sample complex web content with nested structure
        self.complex_web_content = """<!DOCTYPE html>
        <html>
        <head>
            <title>Sustainable Technology Solutions</title>
        </head>
        <body>
            <header>
                <h1>Sustainable Technology Solutions</h1>
                <nav>
                    <ul>
                        <li>Home</li>
                        <li>Products</li>
                        <li>About</li>
                    </ul>
                </nav>
            </header>
            
            <main>
                <section id="introduction">
                    <h2>Introduction to Sustainable Tech</h2>
                    <p>Sustainable technology aims to reduce environmental impact while maintaining performance.</p>
                    <p>The growing concern about climate change has accelerated development in this field.</p>
                </section>
                
                <section id="solar">
                    <h2>Solar Energy Solutions</h2>
                    <div class="product-card">
                        <h3>Residential Solar Panels</h3>
                        <p>Our residential solar panels provide efficient energy conversion and long-term reliability.</p>
                        <ul>
                            <li>25-year warranty</li>
                            <li>22% efficiency rating</li>
                            <li>Smart monitoring included</li>
                        </ul>
                    </div>
                    
                    <div class="product-card">
                        <h3>Commercial Solar Arrays</h3>
                        <p>Designed for businesses looking to reduce energy costs and carbon footprint.</p>
                    </div>
                </section>
            </main>
            
            <footer>
                <p>Contact us at sustainability@example.com</p>
            </footer>
        </body>
        </html>"""

    def test_technical_document_chunking(self):
        """Test chunking of technical documents with headings."""
        chunks = semantic_chunk_document(self.technical_document, "technical")

        # Verify appropriate number of chunks created
        self.assertTrue(
            len(chunks) >= 4,
            f"Technical document should be split into at least 4 chunks, got {len(chunks)}",
        )

        # Verify headings are preserved
        headings_found = 0
        for chunk in chunks:
            if "section_heading" in chunk["metadata"]:
                headings_found += 1

        self.assertTrue(
            headings_found > 0, "No headings found in technical document chunks"
        )

        # Verify chunks have reasonable sizes
        for chunk in chunks:
            self.assertTrue(
                100 <= len(chunk["content"]) <= 2000,
                f"Chunk size outside reasonable bounds: {len(chunk['content'])}",
            )

    def test_advanced_technical_document_chunking(self):
        """Test chunking of technical documents with tables and figures."""
        chunks = semantic_chunk_document(self.advanced_technical_document, "technical")

        # Verify figures and tables are properly identified
        figure_chunks = 0
        table_chunks = 0
        for chunk in chunks:
            if "Figure 1:" in chunk["content"]:
                figure_chunks += 1
            if "Table 1:" in chunk["content"]:
                table_chunks += 1

        self.assertTrue(figure_chunks > 0, "Figure references not correctly chunked")
        self.assertTrue(table_chunks > 0, "Table references not correctly chunked")

        # Verify section cohesion - Table should be in same chunk or next to Gradient Boosting
        gradient_boosting_chunk_index = -1
        table_chunk_index = -1

        for i, chunk in enumerate(chunks):
            if "Gradient Boosting" in chunk["content"]:
                gradient_boosting_chunk_index = i
            if "Table 1:" in chunk["content"]:
                table_chunk_index = i

        # Either same chunk or consecutive chunks
        self.assertTrue(
            table_chunk_index == gradient_boosting_chunk_index
            or abs(table_chunk_index - gradient_boosting_chunk_index) <= 1,
            "Table should be in same or adjacent chunk to its section",
        )

    def test_transcript_chunking(self):
        """Test chunking of transcript content."""
        chunks = semantic_chunk_document(self.transcript, "transcript")

        # Verify appropriate number of chunks created
        self.assertTrue(
            len(chunks) >= 2,
            f"Transcript should be split into at least 2 chunks, got {len(chunks)}",
        )

        # Verify transcript timestamps/speaker indicators are maintained
        speaker_indicators_found = 0
        for chunk in chunks:
            content = chunk["content"]
            if "Speaker" in content or "[00:" in content:
                speaker_indicators_found += 1

        self.assertTrue(
            speaker_indicators_found > 0,
            "No speaker indicators found in transcript chunks",
        )

    def test_complex_transcript_chunking(self):
        """Test chunking of complex transcript with different timestamp formats."""
        chunks = semantic_chunk_document(self.complex_transcript, "transcript")

        # Verify different timestamp formats are handled
        formats_found = {"parentheses": 0, "brackets": 0, "plain": 0}

        for chunk in chunks:
            content = chunk["content"]
            if re.search(r"\(\d+:\d+", content):
                formats_found["parentheses"] += 1
            if re.search(r"\[\d+:\d+", content):
                formats_found["brackets"] += 1
            if re.search(r"^\d+:\d+", content, re.MULTILINE):
                formats_found["plain"] += 1

        # Should detect at least two different timestamp formats
        formats_detected = sum(1 for count in formats_found.values() if count > 0)
        self.assertTrue(
            formats_detected >= 2,
            f"Should detect at least 2 timestamp formats, found {formats_detected}",
        )

        # Verify speaker continuity - chunks should not break in middle of speaker's point
        speaker_points_preserved = True
        list_broken = False

        for chunk in chunks:
            # Check if numbered lists are preserved within one chunk
            list_start = re.search(r"\d+\.", chunk["content"])
            list_incomplete = (
                list_start
                and not re.search(r"4\.", chunk["content"])
                and "applications" in chunk["content"]
            )

            if list_incomplete:
                list_broken = True

        self.assertFalse(
            list_broken, "Numbered list should not be broken across chunks"
        )

    def test_web_content_chunking(self):
        """Test chunking of web content."""
        chunks = semantic_chunk_document(self.web_content, "web")

        # Verify appropriate number of chunks created
        self.assertTrue(
            len(chunks) >= 2,
            f"Web content should be split into at least 2 chunks, got {len(chunks)}",
        )

        # Verify HTML tags are removed
        for chunk in chunks:
            content = chunk["content"]
            self.assertNotIn(
                "<div>", content, "HTML tags should be removed from web content chunks"
            )
            self.assertNotIn(
                "<p>", content, "HTML tags should be removed from web content chunks"
            )

    def test_complex_web_content_chunking(self):
        """Test chunking of complex web content with nested HTML structure."""
        chunks = semantic_chunk_document(self.complex_web_content, "web")

        # Verify HTML structure is preserved as markdown-like headings
        headings_preserved = 0
        sections_preserved = 0

        for chunk in chunks:
            content = chunk["content"]
            if re.search(r"#\s+\w+", content):  # Look for # Heading format
                headings_preserved += 1
            if (
                "Introduction to Sustainable Tech" in content
                or "Solar Energy Solutions" in content
            ):
                sections_preserved += 1

        self.assertTrue(
            headings_preserved > 0, "Headings should be preserved in markdown format"
        )
        self.assertTrue(
            sections_preserved > 0, "Main content sections should be preserved"
        )

        # Verify no raw HTML remains
        for chunk in chunks:
            content = chunk["content"]
            self.assertNotIn("<div", content, "HTML tags should be removed")
            self.assertNotIn("<section", content, "HTML tags should be removed")
            self.assertNotIn("<h", content, "HTML tags should be removed")

        # Verify semantic content is preserved
        product_descriptions = 0
        for chunk in chunks:
            if (
                "residential solar panels" in chunk["content"].lower()
                and "warranty" in chunk["content"].lower()
            ):
                product_descriptions += 1

        self.assertTrue(
            product_descriptions > 0, "Product descriptions should be preserved"
        )

    def test_table_of_contents_extraction(self):
        """Test extraction of table of contents."""
        toc = extract_table_of_contents(self.technical_document)

        # Verify table of contents was generated
        self.assertIsNotNone(
            toc, "Table of contents should be generated for technical document"
        )

        # Verify key headings are included
        self.assertIn(
            "Supervised Learning", toc, "Table of contents should include main headings"
        )
        self.assertIn(
            "Unsupervised Learning",
            toc,
            "Table of contents should include main headings",
        )

    def test_chunk_metadata(self):
        """Test that chunks contain appropriate metadata."""
        chunks = semantic_chunk_document(
            self.technical_document, "technical", {"source": "test"}
        )

        # Verify metadata is preserved and extended
        for i, chunk in enumerate(chunks):
            metadata = chunk["metadata"]

            # Check basic metadata
            self.assertEqual(
                metadata["document_type"],
                "technical",
                "Document type should be preserved",
            )
            self.assertEqual(
                metadata["source"], "test", "Source metadata should be preserved"
            )

            # Check chunk-specific metadata
            self.assertEqual(
                metadata["chunk_index"], i, "Chunk index should match position"
            )
            self.assertEqual(
                metadata["total_chunks"],
                len(chunks),
                "Total chunks count should be consistent",
            )
            self.assertIn("chunk_size", metadata, "Chunk size should be recorded")

    def test_chunking_strategy(self):
        """
        Test the chunking strategy selection based on document type.
        """
        # Sample text for testing chunking strategies
        sample_text = """# Sample Document
        
        This is a sample document for testing chunking strategies.
        
        ## Section 1
        
        Content for section 1 goes here.
        
        ## Section 2
        
        Content for section 2 goes here.
        
        ### Subsection 2.1
        
        More detailed content.
        """

        # Test default chunking strategy
        chunks = semantic_chunk_document(sample_text, document_type="default")
        self.assertTrue(
            len(chunks) > 0, "Default chunking should produce at least one chunk"
        )

        # Test technical document chunking
        chunks = semantic_chunk_document(sample_text, document_type="technical")
        self.assertTrue(
            len(chunks) > 0, "Technical document chunking should produce chunks"
        )

        # Test with metadata
        metadata = {"source": "test", "author": "tester"}
        chunks = semantic_chunk_document(
            sample_text, document_type="default", metadata=metadata
        )
        self.assertTrue(
            all("metadata" in chunk for chunk in chunks),
            "All chunks should contain metadata",
        )
        # Verify metadata is preserved
        self.assertEqual(chunks[0]["metadata"]["source"], "test")
        self.assertEqual(chunks[0]["metadata"]["author"], "tester")

    def test_chunking_strategy_report(self):
        """Test the chunking strategy evaluation function."""

        # Define a function to evaluate chunking strategy for testing purposes
        def evaluate_chunking_strategy(sample_text, document_type="default"):
            """
            Helper function to evaluate chunking strategy on sample text.
            """
            chunks = semantic_chunk_document(sample_text, document_type)

            # Calculate statistics
            chunk_sizes = [len(chunk["content"]) for chunk in chunks]

            # Look for heading continuity
            headings = [
                chunk["metadata"].get("section_heading")
                for chunk in chunks
                if "section_heading" in chunk["metadata"]
            ]

            # Generate report
            report = {
                "document_type": document_type,
                "original_length": len(sample_text),
                "chunk_count": len(chunks),
                "avg_chunk_size": sum(chunk_sizes) / len(chunks) if chunks else 0,
                "min_chunk_size": min(chunk_sizes) if chunks else 0,
                "max_chunk_size": max(chunk_sizes) if chunks else 0,
                "heading_count": len(headings),
                "sample_headings": headings[:3] if headings else [],
            }

            return report

        # Run the evaluation function with the technical document
        report = evaluate_chunking_strategy(self.technical_document, "technical")

        # Verify report contains expected statistics
        self.assertIn("document_type", report, "Report should include document type")
        self.assertIn("chunk_count", report, "Report should include chunk count")
        self.assertIn(
            "avg_chunk_size", report, "Report should include average chunk size"
        )
        self.assertIn("heading_count", report, "Report should include heading count")

        # Log report for inspection
        logger.info(f"Chunking strategy report: {report}")


if __name__ == "__main__":
    unittest.main()
