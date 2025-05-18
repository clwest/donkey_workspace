from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

from characters.models import CharacterProfile


class Image(models.Model):
    """Model for tracking image generation requests."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    GENERATION_TYPES = [
        ("initial", "Initial"),
        ("inpaint", "Inpaint"),
        ("variation", "Variation"),
        ("remix", "Remix"),
        ("scene", "Scene"),  # Custom scene generation for characters
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="images",
        blank=True,
        null=True,
    )
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    prompt = models.TextField()
    negative_prompt = models.TextField(blank=True, null=True)
    applied_prompt_suffix = models.TextField(blank=True, null=True)
    aspect_ratio = models.CharField(
        max_length=10, blank=True, null=True
    )  # e.g., "16:9"
    width = models.PositiveIntegerField(default=512)
    height = models.PositiveIntegerField(default=512)
    num_outputs = models.PositiveIntegerField(default=1)
    steps = models.PositiveIntegerField(default=50)
    guidance_scale = models.FloatField(default=7.5)
    seed = models.PositiveIntegerField(blank=True, null=True)
    engine_used = models.CharField(
        max_length=50, default="stable-diffusion"
    )  # Optional override
    model_used = models.CharField(max_length=100, blank=True, null=True)
    scheduler = models.CharField(max_length=50, default="K_EULER")

    style = models.ForeignKey(
        "PromptHelper",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="images",
    )

    is_favorite = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    file_path = models.TextField(blank=True, null=True)
    output_url = models.URLField(max_length=500, blank=True, null=True)
    output_urls = models.JSONField(blank=True, null=True, default=list)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    alt_text = models.CharField(max_length=300, blank=True, null=True)
    caption = models.TextField(blank=True, null=True)

    is_public = models.BooleanField(default=False)
    generation_type = models.CharField(
        max_length=20, blank=True, null=True, choices=GENERATION_TYPES
    )
    # Backend selection for image generation
    MODEL_BACKEND_CHOICES = [
        ("stability", "Stability.ai (SDXL)"),
        ("replicate-standard", "Replicate - Standard Image"),
        ("replicate-kling", "Replicate - Kling v1.6 Video"),
        ("openai", "OpenAI"),
    ]
    model_backend = models.CharField(
        max_length=50,
        choices=MODEL_BACKEND_CHOICES,
        default="stability",
        help_text="Select which backend model to use for generation",
    )
    # External prediction job ID (for replicate/OpenAI tasks)
    prediction_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="ID of the external generation job (Replicate/OpenAI)",
    )
    was_upscaled = models.BooleanField(default=False)
    was_edited = models.BooleanField(default=False)

    # ✅ New relationship to main Project model
    project = models.ForeignKey(
        "project.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="images",
    )

    # ✅ Existing relationship to ProjectImage for organizational hierarchy
    project_image = models.ForeignKey(
        "ProjectImage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="image_set",
    )

    # Optional: Story association (illustrations)
    story = models.ForeignKey(
        "story.Story",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="illustrations",
    )
    character = models.ForeignKey(
        CharacterProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="images",
    )
    order = models.PositiveIntegerField(null=False)  # Page order
    tags = models.ManyToManyField("mcp_core.Tag", blank=True)

    def __str__(self):
        return self.title or f"Image {self.id}"

    class Meta:
        app_label = "images"
        ordering = ["-created_at"]
        unique_together = ("story", "order")


class SourceImage(models.Model):
    """User-uploaded or manually added images intended for training, inspiration, or reference."""

    PURPOSE_CHOICES = [
        ("training", "Training"),
        ("reference", "Reference"),
        ("inspiration", "Inspiration"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="source_images"
    )
    image_file = models.ImageField(upload_to="source_images/")
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField("TagImage", blank=True, related_name="source_images")
    purpose = models.CharField(
        max_length=20, choices=PURPOSE_CHOICES, default="training"
    )
    is_public = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title or self.image_file.name} ({self.purpose})"


class UpscaleImage(models.Model):
    aspect_ratio = models.CharField(max_length=10, blank=True, null=True)
    request = models.ForeignKey(
        Image, on_delete=models.CASCADE, related_name="upscale_images"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    engine = models.CharField(max_length=100, null=True, blank=True)
    upscale_type = models.CharField(max_length=20)  # "conservative", "creative", "fast"
    output_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        try:
            if not self.aspect_ratio:
                width = getattr(self, "width", None) or getattr(
                    self.request, "width", None
                )
                height = getattr(self, "height", None) or getattr(
                    self.request, "height", None
                )
                if width and height:
                    self.aspect_ratio = f"{int(width)}:{int(height)}"
        except (TypeError, ValueError):
            pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Upscaled ({self.user.username}) for {self.request.id}"


class Edit(models.Model):
    EDIT_TYPE_CHOICES = [
        ("inpaint", "Inpaint"),
        ("variation", "Variation"),
        ("upscale", "Upscale"),
    ]

    request = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="edits")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    edit_type = models.CharField(max_length=20, choices=EDIT_TYPE_CHOICES)
    prompt = models.TextField(blank=True, null=True)
    negative_prompt = models.TextField(blank=True, null=True)
    seed = models.PositiveIntegerField(blank=True, null=True)
    creativity = models.FloatField(blank=True, null=True)
    output_format = models.CharField(max_length=10, blank=True, null=True)
    style_preset = models.CharField(max_length=100, blank=True, null=True)
    output_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.edit_type} Edit by {self.user.username} for Image {self.request.id}"
        )


class PromptHelper(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    # Legacy prompt fields – will be deprecated in favor of versioning
    prompt = models.TextField(
        help_text="The suffix prompt to be applied to base prompts.",
        default="highly detailed, award-winning illustration, dramatic lighting",
    )
    negative_prompt = models.TextField(
        blank=True,
        null=True,
        default="blurry, low-res, cropped, out of frame, watermark, text, logo",
        help_text="Negative prompt to help avoid undesired elements in generation.",
    )
    category = models.CharField(max_length=100, blank=True, null=True)
    tags = models.JSONField(
        default=list, blank=True, help_text="List of tags like ['portrait', 'anime']"
    )
    is_builtin = models.BooleanField(default=False)
    is_fork = models.BooleanField(
        default=False, help_text="Indicates if this style is a fork of another style."
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="forks",
        help_text="The original style this was forked from.",
    )
    is_favorited = models.BooleanField(
        default=False, help_text="Whether the current user has favorited this style."
    )
    image_path = models.ImageField(upload_to="styles/", null=True, blank=True)
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="favorited_styles",
        blank=True,
        help_text="Users who have favorited this style.",
    )

    placements = models.ManyToManyField(
        "PromptPlacement",
        related_name="associated_prompts",
        blank=True,
        help_text="Where this prompt style should be applied (e.g. image, voice, narration)",
    )

    voice_style = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Preferred TTS voice style for this prompt, e.g., 'echo', 'nova', 'custom-fantasy'",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="custom_styles",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    style_preset = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Optional: If used with external APIs like Stability.ai, this field maps to their style_preset.",
    )
    # Reference to the active version of this prompt
    current_version = models.ForeignKey(
        "PromptHelperVersion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Active PromptHelperVersion for this PromptHelper",
    )

    def __str__(self):
        return f"{self.name} – {self.prompt[:30]}..."

    def __repr__(self):
        return f"<PromptHelper: {self.name}>"

    def fork(self, user):
        return PromptHelper.objects.create(
            name=f"{self.name} (forked)",
            description=self.description,
            prompt=self.prompt,
            negative_prompt=self.negative_prompt,
            category=self.category,
            tags=self.tags,
            is_fork=True,
            parent=self,
            created_by=user,
        )

    class Meta:
        app_label = "images"
        verbose_name = "Style Prompt Assistant"
        verbose_name_plural = "Style Prompt Assistants"


class PromptPlacement(models.Model):
    PROMPT_TYPE_CHOICES = [
        ("image", "Image"),
        ("voice", "Voice"),
        ("video", "Video"),
        ("narration", "Narration"),
        ("style", "Visual Style"),
        ("scene", "Scene Descriptor"),
    ]

    name = models.CharField(max_length=100, unique=True)
    prompt_type = models.CharField(max_length=20, choices=PROMPT_TYPE_CHOICES)
    placement = models.CharField(
        max_length=20,
        choices=[
            ("append", "Append"),
            ("replace", "Replace"),
            ("prefix", "Prefix"),
        ],
        default="append",
    )
    is_enabled = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.prompt_type})"


class TagImage(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# Model to track user favorites of themes
class ThemeFavorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    theme = models.ForeignKey("ThemeHelper", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "theme")

    def __str__(self):
        return f"{self.user.username} favorited {self.theme.name}"


class ProjectImage(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_images",  # <- updated name
        blank=True,
        null=True,
    )
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)  # Homepage carousel.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} by {self.user.username}"


class StableDiffusionUsageLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sd_usage_logs",
    )
    # The image related to this usage log (optional)
    image = models.ForeignKey(
        Image,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usage_logs",
    )
    # Estimated credits used for this operation
    estimated_credits_used = models.FloatField(default=0)
    # Timestamp of usage
    created_at = models.DateTimeField(auto_now_add=True)


# PromptHelperVersion model for versioned prompts
class PromptHelperVersion(models.Model):
    helper = models.ForeignKey(
        PromptHelper,
        related_name="versions",
        on_delete=models.CASCADE,
        help_text="The PromptHelper this version belongs to.",
    )
    version_number = models.PositiveIntegerField(
        help_text="Incremental version number for this helper."
    )
    prompt = models.TextField(help_text="The prompt text for this version.")
    negative_prompt = models.TextField(
        blank=True, null=True, help_text="The negative prompt for this version."
    )
    notes = models.TextField(
        blank=True, null=True, help_text="Optional notes about this version."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("helper", "version_number")
        ordering = ["-version_number"]

    def __str__(self):
        return f"{self.helper.name} v{self.version_number}"


# Signal to create initial version when PromptHelper is saved
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=PromptHelper)
def create_initial_prompt_helper_version(sender, instance, created, **kwargs):
    # On creation or if no versions exist, create initial version
    if created or not instance.versions.exists():
        # Determine next version number
        next_version = instance.versions.count() + 1
        version = PromptHelperVersion.objects.create(
            helper=instance,
            version_number=next_version,
            prompt=instance.prompt,
            negative_prompt=instance.negative_prompt,
        )
        # Set current_version on helper if not already set
        if not instance.current_version_id:
            PromptHelper.objects.filter(pk=instance.pk).update(current_version=version)
    image = models.ForeignKey(
        "images.Image", on_delete=models.CASCADE, null=True, blank=True
    )
    prompt = models.TextField()
    estimated_credits_used = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.estimated_credits_used} credits @ {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ThemeHelper(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(
        blank=True, help_text="Brief description of the theme world."
    )

    prompt = models.TextField(help_text="Prompt suffix to apply for this theme.")
    negative_prompt = models.TextField(
        blank=True, help_text="Optional negative prompt to avoid unwanted generations."
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional grouping category (e.g. Environment, Fantasy, Historical)",
    )

    # Tags and visual/style recommendations
    tags = models.JSONField(
        default=list, blank=True, help_text="List of tags to associate with this theme."
    )
    recommended_styles = models.ManyToManyField(
        "PromptHelper",
        blank=True,
        help_text="Suggest visual styles for stories/images in this theme.",
    )

    is_builtin = models.BooleanField(default=False)
    # Whether this theme is visible to all users
    is_public = models.BooleanField(default=False)
    is_fork = models.BooleanField(default=False)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Original theme this was forked from",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="theme_helper",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    # Optional preview image for frontend theme selection
    preview_image = models.ImageField(
        upload_to="theme_previews/", null=True, blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
