from django.urls import path
from . import views

urlpatterns = [
    path("assistants/<uuid:assistant_id>/archetype-card/", views.get_archetype_card),
    path("ritual-launchpads/", views.get_ritual_launchpads),
]
