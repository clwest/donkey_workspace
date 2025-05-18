from celery import shared_task


@shared_task(bind=True)
def train_character_embedding(self, character_id: int):
    """
    Celery task to train and store character embedding using Embedding model and update training profile.
    """
    # Local imports to avoid circular dependencies
    from characters.models import CharacterProfile, CharacterTrainingProfile
    from embeddings.helpers.helpers_processing import generate_embedding
    from embeddings.models import Embedding

    # Task metadata
    task_id = getattr(self.request, "id", None)
    # Fetch the character instance
    character = CharacterProfile.objects.get(id=character_id)
    # Persist initial training status and task ID
    CharacterTrainingProfile.objects.update_or_create(
        character=character,
        defaults={
            "status": "pending",
            "task_id": task_id,
        },
    )
    # Build prompt text and generate embedding vector
    text = character.full_prompt()
    vector = generate_embedding(text) or []
    # Persist the embedding to the Embedding model (PGVector)
    try:
        emb_record = Embedding.objects.create(
            content_type="characterprofile",
            content_id=str(character_id),
            content=text,
            embedding=vector,
        )
    except Exception:
        emb_record = None
    # Update or create the training profile
    status_val = "complete" if vector else "failed"
    CharacterTrainingProfile.objects.update_or_create(
        character=character,
        defaults={
            "embedding": vector,
            "status": status_val,
            "task_id": task_id,
        },
    )
    # Return some info for inspection
    return {
        "task_id": task_id,
        "vector_length": len(vector),
        "status": status_val,
        "embedding_id": getattr(emb_record, "id", None),
    }
