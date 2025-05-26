from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth import get_user_model

from characters.models import CharacterProfile, CharacterTrainingProfile
from characters.tasks import train_character_embedding
from embeddings.models import Embedding, EMBEDDING_LENGTH

class TrainCharacterEmbeddingTaskTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="trainer", password="pw")
        self.character = CharacterProfile.objects.create(name="Test", created_by=self.user)

    @patch("characters.tasks.generate_embedding")
    def test_training_creates_embedding_and_profile(self, mock_gen):
        vector = [0.1] * EMBEDDING_LENGTH
        mock_gen.return_value = vector

        result = train_character_embedding(self.character.id)

        profile = CharacterTrainingProfile.objects.get(character=self.character)
        self.assertEqual(profile.status, "complete")
        self.assertEqual(profile.embedding, vector)
        emb = Embedding.objects.filter(content_id=str(self.character.id)).first()
        self.assertIsNotNone(emb)
        self.assertEqual(result["vector_length"], len(vector))
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["embedding_id"], str(emb.id))

