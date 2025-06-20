import warnings
warnings.warn("Deprecated; use /api/v1/... endpoints", DeprecationWarning)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_info),
    path('me/assistant/', views.me_assistant),
    path('me/agents/', views.me_agents),
    path('me/documents/', views.me_documents),
    path('me/images/', views.me_images),
    path('me/summary/', views.me_summary),
    path('demo_login/', views.demo_login),
    path('demo/', views.demo_user),

    # Tour completion route mounted under /api/users/
    path('<int:id>/tours/complete/', views.complete_tour),
    path('profile/onboarding_status/', views.onboarding_status),

]
