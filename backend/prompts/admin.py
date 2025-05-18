from django.contrib import admin
from .models import Prompt, PromptPreferences
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from .views import reembed_all_prompts


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "created_at")
    search_fields = ("title", "content", "source")
    actions = ["reembed_selected_prompts"]
    list_filter = ("type", "tone", "model_backend", "is_draft")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "reembed/",
                self.admin_site.admin_view(self.reembed_prompts),
                name="prompts_reembed",
            ),
        ]
        return custom_urls + urls

    def reembed_prompts(self, request):
        """
        Admin action to trigger reembedding for all prompts.
        """
        response = reembed_all_prompts(request)
        messages.success(
            request,
            f"Reembedded {response.data.get('reembedded', 0)} prompts successfully!",
        )
        return redirect(reverse("admin:prompts_prompt_changelist"))

    def reembed_selected_prompts(self, request, queryset):
        """
        Admin action to reembed only selected prompts.
        """
        updated = 0
        from prompts.utils.embeddings import get_embedding
        from embeddings.helpers.helpers_io import save_embedding

        for prompt in queryset:
            try:
                embedding = get_embedding(prompt.content)
                prompt.embedding = embedding
                prompt.save()
                save_embedding(prompt, embedding)
                updated += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Failed to embed {prompt.title}: {str(e)}",
                    level=messages.ERROR,
                )

        self.message_user(
            request, f"Reembedded {updated} selected prompts successfully."
        )


@admin.register(PromptPreferences)
class PromptPreferencesAdmin(admin.ModelAdmin):
    list_display = ("user", "auto_mode_enabled", "updated_at")
