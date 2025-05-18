from django.db import models
from django.conf import settings


class CharacterProfile(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # unique URL-friendly identifier for deep-linking
    # URL-friendly unique identifier for deep-linking (nullable for migrations)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    personality_traits = models.JSONField(default=list, blank=True)
    backstory = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_characters",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # Optional association to a Project
    project = models.ForeignKey(
        "project.Project",
        on_delete=models.CASCADE,
        related_name="characters",
        null=True,
        blank=True,
    )
    # Allow multiple visual styles for this character
    character_styles = models.ManyToManyField(
        "images.PromptHelper",
        blank=True,
        related_name="characters",
    )

    def __str__(self):
        return self.name

    def full_prompt(self) -> str:
        """
        Build a combined prompt string for embedding, including name,
        description, backstory, and personality traits.
        """
        parts = [self.name]
        if self.description:
            parts.append(self.description)
        if self.backstory:
            parts.append(f"Backstory: {self.backstory}")
        if self.personality_traits:
            # personality_traits is a list of strings
            traits = ", ".join(self.personality_traits)
            parts.append(f"Traits: {traits}")
        return " ".join(parts)

    def save(self, *args, **kwargs):
        # Auto-generate a unique slug based on name if not set
        if not self.slug:
            from django.utils.text import slugify

            base_slug = slugify(self.name)
            unique_slug = base_slug
            suffix = 1
            while CharacterProfile.objects.filter(slug=unique_slug).exists():
                suffix += 1
                unique_slug = f"{base_slug}-{suffix}"
            self.slug = unique_slug
        super().save(*args, **kwargs)

    @property
    def primary_image(self):
        # Return the first uploaded reference image (if any)
        return self.reference_images.order_by("created_at").first()


class CharacterStyle(models.Model):
    character = models.ForeignKey(
        CharacterProfile, on_delete=models.CASCADE, related_name="styles"
    )
    style_name = models.CharField(max_length=100)
    prompt_helper = models.ForeignKey(
        "images.PromptHelper",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="character_styles",
        help_text="Optional prompt helper style to apply to this character style.",
    )
    prompt = models.TextField()
    negative_prompt = models.TextField(blank=True, null=True)
    image_reference = models.ImageField(
        upload_to="character_styles/", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.character.name} – {self.style_name}"

    def save(self, *args, **kwargs):
        # If linked to a PromptHelper, populate blank prompts from it
        if self.prompt_helper:
            # Only set prompt if blank or whitespace
            if not self.prompt or not str(self.prompt).strip():
                self.prompt = self.prompt_helper.prompt or ""
            # Only set negative_prompt if blank or None
            if not self.negative_prompt or not str(self.negative_prompt).strip():
                # Ensure a string value
                self.negative_prompt = self.prompt_helper.negative_prompt or ""
        super().save(*args, **kwargs)


class CharacterReferenceImage(models.Model):

    character = models.ForeignKey(
        CharacterProfile, on_delete=models.CASCADE, related_name="reference_images"
    )
    image = models.ImageField(upload_to="character_references/")
    caption = models.CharField(max_length=255, blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Semantic tags extracted/generated for this reference image
    tags = models.ManyToManyField(
        "images.TagImage",
        blank=True,
        related_name="reference_images",
    )
    # Optional visual style for this reference image
    style = models.ForeignKey(
        "images.PromptHelper",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="character_reference_images",
    )
    # Mark primary reference image for character
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.character.name}"


class CharacterTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    characters = models.ManyToManyField(CharacterProfile, related_name="tags")

    def __str__(self):
        return self.name


class CharacterTrainingProfile(models.Model):
    character = models.OneToOneField(
        "characters.CharacterProfile",
        on_delete=models.CASCADE,
        related_name="training_profile",
    )
    embedding = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("training", "Training"),
            ("complete", "Complete"),
            ("failed", "Failed"),
        ],
        default="pending",
    )
    task_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"TrainingProfile: {self.character.name} ({self.status})"


# Automatically create a training profile when a new CharacterProfile is created
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=CharacterProfile)
def create_training_profile(sender, instance, created, **kwargs):
    if created:
        CharacterTrainingProfile.objects.create(character=instance)
