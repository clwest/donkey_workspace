# from embeddings.utils import embed_text
# from mcp_core.models import DevDoc

# for doc in DevDoc.objects.filter(embedding__isnull=True):
#     doc.embedding = embed_text(doc.content)
#     doc.save()
#     print(f"✅ Embedded {doc.slug}")