from django.urls import path
from . import views

urlpatterns = [
    path('me/assistant/', views.me_assistant),
    path('me/agents/', views.me_agents),
    path('me/documents/', views.me_documents),
    path('me/images/', views.me_images),
    path('me/summary/', views.me_summary),
]
