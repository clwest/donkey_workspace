# Assistant URLS

path("", views.assistants_view, name="assistants_view"),
path("create/", views.assistants_view, name="assistants-list-create"),
path("projects/", views.assistant_projects, name="assistant-projects"), # GET (list) + POST (create)
path("projects/<uuid:pk>/", views.assistant_project_detail, name="assistant-project-detail"), # GET, PATCH, DELETE
path("projects/<uuid:project_id>/tasks/", views.assistant_project_tasks),
path("tasks/<uuid:task_id>/", views.assistant_project_task_detail),
path("projects/<uuid:project_id>/generate_tasks/", views.generate_tasks_for_project),
path("projects/tasks/<int:task_id>/", views.update_or_delete_task, name="update_or_delete_task"),
path("objectives/<uuid:objective_id>/actions/", views.assistant_next_actions, name="assistant-next-actions"),
path("projects/<slug:slug>/thoughts/", views.assistant_project_thoughts, name="project-thoughts"), # GET + POST
path("projects/<slug:slug>/thoughts/<int:thought_id>/", views.assistant_update_project_thought, name="update-project-thought"), # PATCH
path("projects/<slug:slug>/thoughts/generate/", views.generate_assistant_project_thought, name="generate-assistant-thought"), # POST
path("projects/<slug:slug>/thoughts/reflect/", views.assistant_reflect_on_thoughts, name="reflect-on-thoughts"), # POST
path("projects/<uuid:project_id>/reflections/", views.assistant_reflection_insights, name="assistant-reflection-insights"), # GET + POST
path("projects/link_prompt/", views.link_prompt_to_project, name="link-prompt-to-project"), # POST
path("projects/<uuid:project_id>/linked_prompts/", views.linked_prompts, name="linked-prompts"), # GET
path("projects/<uuid:pk>/ai_plan/", views.ai_plan_project, name="ai-plan-project"), # POST
path("projects/generate-mission/", views.generate_project_mission, name="generate-project-mission"), # POST
path("projects/link_memory/", views.link_memory_to_project, name="link-memory-to-project"), # POST
path("projects/<uuid:project_id>/linked_memories/", views.linked_memories, name="linked-memories"), # GET
path("projects/<uuid:project_id>/memory-chains/", views.assistant_memory_chains, name="assistant-memory-chains"), # GET + POST
path("sources/", views.signal_sources, name="signal-sources"), # GET + POST
path("signals/", views.signal_catches, name="signal-catches"), # GET
path("signals/create/", views.create_signal_catch, name="create-signal-catch"), # POST
path("signals/<uuid:pk>/", views.update_signal_catch, name="update-signal-catch"),
path("demos/", views.demo_assistant, name="demo_assistant"),
path('sessions/list/', views.list_chat_sessions, name='chat_session_list'),
path('sessions/detail/<str:session_id>/', views.chat_session_detail, name='chat_session_detail'),
path("messages/feedback/", views.submit_chat_feedback, name="submit_chat_feedback"),
path("messages/<uuid:uuid>/update/", views.update_message_feedback, name="update_message_feedback"),

## SLUGS MUST STAY AT THE BOTTOM!

path("<slug:slug>/chat/", views.chat_with_assistant_view, name="assistant-chat"),
path("<slug:slug>/log_thought/", views.log_assistant_thought, name="log-assistant-thought"),
path("<slug:slug>/thoughts/", views.assistant_thoughts_by_slug, name="assistant_thoughts_by_slug"),
path("<slug:slug>/reflect/", views.reflect_on_assistant_thoughts, name="assistant_reflect_on_thoughts"),
path("<slug:slug>/submit-thought/", views.submit_assistant_thought, name="submit-assistant-thought"),
path("<slug:slug>/", views.assistant_detail_view, name="assistant-detail"),

# Characters

# characters/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
CharacterProfileViewSet,
CharacterStyleViewSet,
CharacterReferenceImageViewSet,
CharactersByProjectView,
CharacterSimilarityView,
CharacterTrainView,
CharacterTrainingStatusView,
CharacterProfileSimilarityView,
CharacterImagesView,
NameGenerationView,
)

router = DefaultRouter()
router.register(r'profiles', CharacterProfileViewSet, basename='characterprofile')
router.register(r'styles', CharacterStyleViewSet)
router.register(r'reference-images', CharacterReferenceImageViewSet)

urlpatterns = [
path('', include(router.urls)),

# Character name generation via OpenAI

path('names/generate/', NameGenerationView.as_view(), name='generate-character-name'),

# List characters under a specific project

path(
'projects/<int:pk>/characters/',
CharactersByProjectView.as_view(),
name='project-characters'
),

# Semantic similarity search

path(
'similarity/',
CharacterSimilarityView.as_view(),
name='character-similarity'
),

# Trigger embedding training task for a character

path(
'profiles/<int:pk>/train/',
CharacterTrainView.as_view(),
name='character-train'
),

# Training status endpoint

path(
'profiles/<int:pk>/train_status/',
CharacterTrainingStatusView.as_view(),
name='character-training-status'
),

# Find similar characters for a given profile

path(
'profiles/<int:pk>/similar/',
CharacterProfileSimilarityView.as_view(),
name='character-profile-similarity'
),

# List reference images for a given profile

path(
'profiles/<int:pk>/images/',
CharacterImagesView.as_view(),
name='character-profile-images'
),
]

# Embedding URLS

# === Core Embedding Tools ===

path("embed-text/", api_views.embed_text_api, name="embed-text"),
path("chunk-text/", api_views.chunk_text_api, name="chunk-text"),
path("search/", api_views.search_embeddings, name="search-embeddings"),
path("search-targets/", api_views.list_search_targets, name="search-targets"),

# === Session Tools ===

path("session/<str:session_id>/documents/", api_views.session_docs_api, name="session-docs"),
path("track-session/", api_views.track_session_api, name="track-session"),

# === Legacy / Specific Tools ===

path("similar/", api_views.search_similar_embeddings_api, name="search-similar"),
path("similar-characters/", api_views.search_similar_characters, name="search-similar-characters"),

# Images URL

from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import path, include
from . import debugger

# images/urls.py

from rest_framework.routers import DefaultRouter
from images.views import (
ImageViewSet,
UserImageView,
PublicImageViewSet,
EditImageViewSet,
StyleViewSet,
UpscaleImageView,
TagImageViewSet,
ProjectImageViewSet,
StableDiffusionGenerationView,
CheckImageStatusView,
PromptHelperViewSet,
ProjectImageGalleryView,
ThemeHelperViewSet,
ThemeFavoriteViewSet
)
from images.views import NarrateSceneView
from images.views import PromptHelperSimilarityView

router = DefaultRouter()
router.register(r'gallery', PublicImageViewSet, basename='public-images')
router.register(r'user-images', UserImageView, basename='user-images')
router.register(r'images', ImageViewSet, basename='images')
router.register(r'edit', EditImageViewSet, basename='edit')
router.register(r'upscale', UpscaleImageView, basename='upscale')
router.register(r'styles', StyleViewSet, basename='styles')
router.register(r'tags', TagImageViewSet, basename='tags')
router.register(r'image-projects', ProjectImageViewSet, basename='image-projects')
router.register(r"prompt-helpers", PromptHelperViewSet, basename="prompt-helpers")
router.register(r'theme-helpers', ThemeHelperViewSet, basename='themehelper')
router.register(r'theme-favorites', ThemeFavoriteViewSet, basename='themefavorite')

# Custom views that aren't model-based

custom_views = [
path('generate/', StableDiffusionGenerationView.as_view({'post': 'create'}), name='sd-generate'),
path('status/<int:pk>/', CheckImageStatusView.as_view({'get': 'retrieve'}), name='sd-status'),
]

urlpatterns = [
path("debug/prompts/", debugger.debug_prompts, name="debug-prompts"),
]
urlpatterns += router.urls + custom_views

# Project gallery endpoint

urlpatterns += [
path(
"projects/<int:project_id>/gallery/",
ProjectImageGalleryView.as_view(),
name="project-gallery"
),
]
urlpatterns += [

# TTS narration for scene images

path('images/<int:pk>/narrate/', NarrateSceneView.as_view(), name='image-narrate'),
]
urlpatterns += [

# Semantic similarity for PromptHelpers

path(
'prompt-helpers/similar/',
PromptHelperSimilarityView.as_view(),
name='prompt-helper-similarity'
),
]

# MCP_CORE URLS

from django.urls import path
from mcp_core import views

urlpatterns = [
path("prompt-usage/", views.log_prompt_usage_view, name="log-prompt-usage"),
path('reflect/', views.reflect_on_memories, name='reflect-on-memories'),
path('reflections/<int:reflection_id>/save/', views.save_reflection),
path('reflections/', views.list_reflections),
path('reflections/<int:reflection_id>/', views.reflection_detail),
path('reflections/<int:pk>/expand/', views.expand_reflection, name="expand-reflection"),
path('reflection-tags/<str:tag_name>/', views.reflections_by_tag, name="reflections-by-tag"),
path('top-tags/', views.top_tags, name="top-tags"),
path('reflections/recent/', views.recent_reflections, name='recent-reflections'),
path('reflect/custom/', views.reflect_on_custom_memories, name='reflect-on-custom-memories'),
path('memories/', views.list_memories, name='list-memories'),

     path("agent/", views.list_agent, name="list-agent"),
     path("agent/<slug:slug>/", views.agent_detail, name="agent-detail"),
     path('agent/<uuid:agent_id>/reflect/', views.reflect_on_agent_project, name='reflect-on-agent'),
     path("agent/projects/<uuid:project_id>/reflections/", views.project_reflections, name='agent-project-reflection'),

]

# Memory URLS

path("save/", views.save_memory, name="save_memory"),
path("recent/", views.recent_memories, name="recent_memories"),
path('list/', views.list_memories, name='list_memories'),
path("reflect/", views.reflect_on_memory, name="reflect-on-memory"),
path("chains/create/", views.create_memory_chain, name="create_memory_chain"),
path("chains/<uuid:pk>/", views.get_memory_chain, name="get_memory_chain"),
path("chains/list/", views.list_memory_chains, name="list_memory_chains"),
path("reflect-on-memories/", views.reflect_on_memories, name="reflect_on_memories"),
path("reflection/", views.save_reflection, name="save-reflection"),
path("upload-voice/", views.upload_voice_clip, name="upload_voice_clip"),
path("memory/<uuid:memory_id>/feedback/", views.list_memory_feedback, name="memory-feedback-list"),
path("memory/feedback/submit/", views.submit_memory_feedback, name="memory-feedback-submit"),
path("<uuid:id>/", views.memory_detail, name="memory_detail"),
path("by-tag/<slug:slug>/", views.memories_by_tag),
path("update-tags/<uuid:id>/", views.update_memory_tags),
path("replace/<uuid:id>/", views.replace_memory),
path("assistants/<slug:slug>/memories/", views.assistant_memories, name="assistant-memories"),

# Project URLS

# project/urls.py

from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet
from django.urls import path
from story.views import ProjectStoriesViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename="projects")

urlpatterns = router.urls + [

# Nested routes for project-specific stories

path(
'projects/<int:project_pk>/stories/',
ProjectStoriesViewSet.as_view({'get': 'list', 'post': 'create'}),
name='project-stories-list'
),
path(
'projects/<int:project_pk>/stories/<int:pk>/',
ProjectStoriesViewSet.as_view({
'get': 'retrieve',
'put': 'update',
'patch': 'partial_update',
'delete': 'destroy'
}),
name='project-stories-detail'
),
]

# Prompt URLS

from django.urls import path
from . import views

urlpatterns = [
path("", views.list_prompts),
path("tags/", views.list_prompt_tags),
path("preferences/", views.get_my_prompt_preferences),
path("preferences/update/", views.update_my_prompt_preferences),
path("reduce/", views.reduce_prompt),
path("split/", views.split_prompt),
path("auto-reduce/", views.auto_reduce_prompt_view),
path("analyze/", views.analyze_prompt),
path("mutate-prompt/", views.mutate_prompt_view),
path("mutate/", views.mutate_prompt_view),
path("generate-from-idea/", views.generate_prompt_from_idea_view),
path("create/", views.create_prompt),

# path("search/", views.prompt_search, name="prompt-search"),

path("reembed/", views.reembed_all_prompts),
path("<slug:slug>/", views.prompt_detail),
]

# Story URLS

from rest_framework.routers import DefaultRouter
from .views import StoryViewSet

router = DefaultRouter()
router.register(r'', StoryViewSet, basename='stories')

urlpatterns = router.urls
from .views import StoryViewSet
from django.urls import path

# Additional actions on StoryViewSet

urlpatterns += [
path(
'<int:pk>/tag-chunks/',
StoryViewSet.as_view({'post': 'tag_chunks'}),
name='story-tag-chunks'
),
path(
'<int:pk>/chunk-tags/',
StoryViewSet.as_view({'get': 'chunk_tags'}),
name='story-chunk-tags'
),

# Aggregate top tags from story chunks

path(
'<int:pk>/tags/',
StoryViewSet.as_view({'get': 'tags'}),
name='story-tags'
),
]

# React/Vite URLS

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";

import PromptsPage from "./pages/prompts/PromptsPage";
import PromptDetailView from "./pages/prompts/PromptDetailView";
import PromptRemixPage from "./pages/prompts/PromptRemixPage";
import CreatePromptPage from "./pages/prompts/CreatePromptPage";
import PromptCreationAssistant from "./pages/assistant/prompts/PromptCreationAssistant";

// MCP_CORE
import ReflectionPage from './pages/mcp_core/reflections/ReflectionPage';
import ReflectionHistoryPage from "./pages/mcp_core/reflections/ReflectionHistoryPage";
import ReflectionDetailPage from "./pages/mcp_core/reflections/ReflectionDetailPage";
import ReflectionTagsPage from "./pages/mcp_core/reflections/ReflectionTagsPage";
import HotTagsPage from "./pages/mcp_core/reflections/HotTagsPage";
import RecentReflectionsPage from "./pages/mcp_core/recent/RecentReflectionsPage";
import CustomReflectionPage from "./pages/mcp_core/reflections/CustomReflectionPage";
import ChatWithAgentPage from "./pages/mcp_core/agents/ChatWithAgentPage";
// import AgentDemosPage from "./pages/mcp_core/agents/AgentDemosPage";
// import AgentDashboardPage from "./pages/mcp_core/agents/AgentDashboardPage";
// import AgentDetailPage from "./pages/mcp_core/agents/AgentDetailPage"
// import AgentList from "./pages/mcp_core/agents/AgentList";
// import AgentStatsWidget from "./pages/mcp_core/agents/AgentStatsWidget"
// import AgentThoughtsPage from "./pages/mcp_core/agents/AgentThoughtsPage";
// import CreateNewAgent from "./pages/mcp_core/agents/ChatWithAgentPage";

{/_User Memories _/}
import MemoryBrowserPage from "./pages/memories/entries/MemoryBrowserPage";
import MemoryDetailPage from "./pages/memories/entries/MemoryDetailPage";
import MemoryReflectionPage from "./pages/memories/reflections/MemoryReflectionPage";
import MemoryChainBuilderPage from "./pages/memories/chains/MemoryChainBuilderPage";
import MemoryChainViewerPage from "./pages/memories/chains/MemoryChainViewerPage";
import MemoryChainsListPage from "./pages/memories/chains/MemoryChainsListPage";
import MemoryChainDetailPage from "./pages/memories/chains/MemoryChainDetailPage"; // 👈 ADD THIS
import MemoryEntryCreatePage from "./pages/memories/entries/MemoryEntryCreatePage";

{/\*_ Assistant _/}
import AssistantDashboardPage from "./pages/assistant/common/AssistantDashboardPage";
import AssistantList from "./pages/assistant/common/AssistantList";
import AssistantDetailPage from "./pages/assistant/common/AssistantDetailPage";
import AssistantThoughtsPage from "./pages/assistant/common/AssistantThoughtsPage";
import AssistantDemoPage from "./pages/assistant/common/AssistantDemoPage";
import ChatWithAssistantPage from "./pages/assistant/common/ChatWithAssistantPage";
import CreateNewAssistantPage from "./pages/assistant/common/CreateNewAssistantPage";

import ProjectDetailPage from "./pages/assistant/projects/ProjectDetailPage";
import ProjectCreateFromMemoryPage from "./pages/assistant/projects/ProjectCreateFromMemoryPage";
import CreateProjectPage from "./pages/assistant/projects/CreateProjectPage";
import ProjectMissionBuilderPage from "./pages/assistant/projects/ProjectMissionBuilderPage";
import ProjectTaskBuilderPage from "./pages/assistant/projects/ProjectTaskBuilderPage";
import ProjectTaskEditor from "./pages/assistant/projects/ProjectTaskEditorPage";
import ProjectsDashboardPage from "./pages/assistant/projects/ProjectsDashboardPage";
import ProjectStatusBoardPage from "./pages/assistant/projects/ProjectStatusBoardPage";
import ProjectTaskManagerPage from "./pages/assistant/projects/ProjectTaskManagerPage";
import ProjectTimelinePage from "./pages/assistant/milestones/ProjectTimelinePage";
import ProjectObjectivesPage from "./pages/assistant/projects/ProjectObjectivesPage";
import AssistantThoughtLogPage from "./pages/assistant/thoughts/AssistantThoughtLogPage";
import ProjectThoughtLog from "./pages/assistant/thoughts/ProjectThoughtLog";
import AssistantMemoriesPage from "./pages/assistant/common/AssistantMemoriesPage"
import AssistantMemoryPage from "./pages/assistant/memory/AssistantMemoryPage";
import MemoryToTaskPage from "./pages/assistant/objectives/MemoryToTaskPage";
import MilestonesPage from "./pages/assistant/milestones/MilestonesPage";
import MilestoneCreatePage from "./pages/assistant/milestones/MilestoneCreatePage";
import MilestoneEditPage from "./pages/assistant/milestones/MilestoneEditPage";
import MemoryChainsPage from "./pages/assistant/memory_chains/MemoryChainsPage";
import ReflectionsPage from "./pages/assistant/reflections/ReflectionsPage";
import NextActionsPage from "./pages/assistant/objectives/NextActionsPage";
import ObjectivesPage from "./pages/assistant/objectives/ObjectivesPage";
import AssistantSessionsPage from "./pages/assistant/sessions/AssistantSessionsPage";
import AssistantSessionDetailPage from "./pages/assistant/sessions/AssistantSessionDetailPage"

import SignalSourcesPage from "./pages/assistant/signal_sources/SignalSourcesPage";
import SignalCatchesPage from "./pages/assistant/signal_catches/SignalCatchesPage";

import { ToastContainer } from "react-toastify";
import Navbar from './components/Navbar';
import "react-toastify/dist/ReactToastify.css";

export default function App() {
return (
<Router>

      <div>
      <ToastContainer position="bottom-right" autoClose={3000} />
      <Navbar />

        <Routes>
          {/* Prompts */}
          <Route path="/" element={<HomePage />} />
          <Route path="/prompts" element={<PromptsPage />} />
          <Route path="/prompts/:slug/remix" element={<PromptRemixPage />} />
          <Route path="/prompts/:slug" element={<PromptDetailView />} />
          <Route path="/prompts/create" element={<CreatePromptPage />} />
          <Route path="/prompts/assistant" element={<PromptCreationAssistant />} />

          {/* Memories */}
          <Route path="/memories/new" element={<MemoryEntryCreatePage />} />
          <Route path="/memories" element={<MemoryBrowserPage />} /> {/* ➕ */}
          <Route path="/memories/:id" element={<MemoryDetailPage />} /> {/* 🧠 */}
          <Route path="/memories/reflect" element={<MemoryReflectionPage />} />
          <Route path="/memories/chains" element={<MemoryChainsListPage />} />
          <Route path="/memories/chains/create" element={<MemoryChainBuilderPage />} />
          <Route path="/memories/chains/:id" element={<MemoryChainViewerPage />} />
          <Route path="/memories/chain/:id" element={<MemoryChainDetailPage />} /> {/* 🔗 Chain Viewer */}

          {/* Assistant & Projects */}
          <Route path="/assistants" element={<AssistantList />} />
          <Route path="/assistants/create" element={<CreateNewAssistantPage />} />
          <Route path="/assistants/:slug" element={<AssistantDetailPage />} />
          <Route path="/assistants/projects/create" element={<CreateProjectPage />} />
          <Route path="/assistant-dashboard" element={<AssistantDashboardPage />} />
          <Route path="/assistants/:slug/chat" element={<ChatWithAssistantPage />} />
          <Route path="/assistants/projects" element={<ProjectsDashboardPage />} />
          <Route path="/assistants/projects/:id" element={<ProjectDetailPage />} />
          <Route path="/assistants/projects/create-from-memory" element={<ProjectCreateFromMemoryPage />} />
          <Route path="/assistants/projects/:id/build" element={<ProjectTaskBuilderPage />} />
          <Route path="/assistants/projects/:id/edit-tasks" element={<ProjectTaskEditor />} />
          <Route path="/assistants/projects/:id/tasks" element={<ProjectTaskManagerPage />} />
          <Route path="/assistants/projects/:id/status-board" element={<ProjectStatusBoardPage />} />
          <Route path="/assistants/projects/:id/mission" element={<ProjectMissionBuilderPage />} />
          <Route path="/assistants/projects/:projectId/timeline" element={<ProjectTimelinePage />} />
          <Route path="/assistants/projects/:projectId/objectives" element={<ProjectObjectivesPage />} />
          <Route path="/assistants/sources" element={<SignalSourcesPage />} />
          <Route path="/assistants/signals" element={<SignalCatchesPage />} />
          {/* Assistant Projects Milestones */}
          <Route path="/assistants/projects/:projectId/milestones" element={<MilestonesPage />} />
          <Route path="/assistants/projects/:projectId/milestones/create" element={<MilestoneCreatePage />} />
          <Route path="/assistants/projects/:projectId/milestones/:milestoneId/edit" element={<MilestoneEditPage />} />

          {/*Assistants Thoughts */}
          <Route path="/assistant/projects/:id/thoughts" element={<ProjectThoughtLog />} />
          <Route path="/assistants/:slug/log_thought" element={<AssistantThoughtLogPage />} />

          <Route path="/assistants/:slug/memories" element={<AssistantMemoriesPage />} />
          <Route path="/assistants/:slug/memories" element={<AssistantMemoryPage />} />
          {/* Assistant Objectives */}
          <Route path="/assistants/:slug/objectives" element={<ObjectivesPage />} />
          <Route path="/assistants/next-actions" element={<NextActionsPage />} />
          <Route path="/assistants/memory/:memoryId/to-task" element={<MemoryToTaskPage />} />
          <Route path="/assistants/memory-chains" element={<MemoryChainsPage />} />
          <Route path="/assistants/reflections" element={<ReflectionsPage />} />
          <Route path="/assistants/sessions" element={<AssistantSessionsPage />} />
          <Route path="/assistants/sessions/:sessionId" element={<AssistantSessionDetailPage />} />
          <Route path="/assistants/:slug/thoughts" element={<AssistantThoughtsPage />} />
          <Route path="/assistants-demos" element={<AssistantDemoPage />} />

          {/* MCP Core */}
          <Route path="/reflect" element={<ReflectionPage />} />
          <Route path="/reflections" element={<ReflectionHistoryPage />} />
          <Route path="/reflections/:id" element={<ReflectionDetailPage />} />
          <Route path="/reflection-tags" element={<ReflectionTagsPage />} />
          <Route path="/reflection-tags/:tag" element={<ReflectionTagsPage />} />
          <Route path="/hot-tags" element={<HotTagsPage />} />
          <Route path="/recent-reflections" element={<RecentReflectionsPage />} />
          <Route path="/reflections/custom" element={<CustomReflectionPage />} />


        </Routes>
      </div>
    </Router>

);
}
