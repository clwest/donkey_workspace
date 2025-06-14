from django.core.management.base import BaseCommand
from intel_core.models import DocumentChunk, DocumentTopicSet
from memory.models import SymbolicMemoryAnchor
from django.utils.text import slugify
from collections import Counter
import numpy as np

try:
    from sklearn.cluster import KMeans
except Exception:
    KMeans = None

class Command(BaseCommand):
    help = "Group document chunks by embedding similarity"

    def add_arguments(self, parser):
        parser.add_argument('--clusters', type=int, default=5)

    def handle(self, *args, **options):
        if KMeans is None:
            self.stderr.write('sklearn not installed')
            return
        cluster_count = options['clusters']
        chunks = DocumentChunk.objects.filter(embedding__isnull=False).select_related('embedding')
        vectors = []
        chunk_list = []
        for c in chunks:
            vec = c.embedding.vector if c.embedding else None
            if vec:
                vectors.append(vec)
                chunk_list.append(c)
        if not vectors:
            self.stdout.write('No embedded chunks found')
            return
        vectors = np.array(vectors)
        kmeans = KMeans(n_clusters=min(cluster_count, len(vectors)), n_init=10, random_state=42)
        labels = kmeans.fit_predict(vectors)
        grouped = {}
        for label, chunk in zip(labels, chunk_list):
            grouped.setdefault(label, []).append(chunk)
        for label, cks in grouped.items():
            words = ' '.join([c.text for c in cks]).split()
            common = [w for w,_ in Counter(words).most_common(3)]
            title = ' '.join(common) if common else f'Topic {label}'
            slug = slugify(title)[:50]
            anchor, _ = SymbolicMemoryAnchor.objects.get_or_create(
                slug=slug,
                defaults={
                    'label': title[:100],
                    'source': 'auto',
                    'created_from': 'topic_cluster',
                },
            )
            topic_set = DocumentTopicSet.objects.create(
                title=title[:255],
                description=f'Auto cluster {label}',
                auto_suggested_anchor=anchor,
            )
            topic_set.related_chunks.set(cks)
            self.stdout.write(f'Created {topic_set.title} with {len(cks)} chunks')
