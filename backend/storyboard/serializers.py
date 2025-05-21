from rest_framework import serializers
from .models import NarrativeEvent
from images.serializers import ImageSerializer
from videos.serializers import VideoSerializer
from tts.serializers import StoryAudioSerializer
from characters.serializers import CharacterProfileSerializer
from story.serializers import StorySerializer


class NarrativeEventSerializer(serializers.ModelSerializer):
    linked_image = ImageSerializer(read_only=True)
    linked_video = VideoSerializer(read_only=True)
    linked_tts = StoryAudioSerializer(read_only=True)
    linked_character = CharacterProfileSerializer(read_only=True)
    linked_story = StorySerializer(read_only=True)

    class Meta:
        model = NarrativeEvent
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
