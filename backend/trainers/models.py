# trainers/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ReplicateModel(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.version})"


class ReplicatePrediction(models.Model):
    STATUS_CHOICES = [
        ("starting", "Starting"),
        ("processing", "Processing"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
        ("canceled", "Canceled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="predictions")
    model = models.ForeignKey(
        ReplicateModel, on_delete=models.CASCADE, related_name="predictions"
    )
    prediction_id = models.CharField(max_length=255, unique=True)
    prompt = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    num_outputs = models.IntegerField(default=1)
    files = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.prediction_id} ({self.status})"
