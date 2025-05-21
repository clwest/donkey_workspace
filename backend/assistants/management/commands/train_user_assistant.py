from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from intel_core.models import Document
from images.models import SourceImage
from embeddings.helpers.helpers_processing import generate_embedding

class Command(BaseCommand):
    help = "Train a user's personal assistant from uploaded documents and images"

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, required=True)

    def handle(self, *args, **options):
        User = get_user_model()
        user_id = options['user_id']
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise CommandError('User not found')

        assistant = getattr(user, 'personal_assistant', None)
        if not assistant:
            self.stdout.write(self.style.ERROR('User has no personal assistant'))
            return

        documents = Document.objects.filter(user=user)
        images = SourceImage.objects.filter(user=user)

        for doc in documents:
            emb = generate_embedding(doc.content)
            if emb:
                doc.metadata['embedding'] = emb
                doc.save(update_fields=['metadata'])
            assistant.documents.add(doc)

        for img in images:
            text = img.description or img.title or ''
            if text:
                generate_embedding(text)

        self.stdout.write(self.style.SUCCESS('Training data processed'))
