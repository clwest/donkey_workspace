import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/auth/LoginPage";
import RegisterPage from "./pages/auth/RegisterPage";
import ProfilePage from "./pages/auth/ProfilePage";
import LogoutPage from "./pages/auth/LogoutPage";
import OnboardingWizardPage from "./pages/onboarding/OnboardingWizardPage";
import RitualOnboardingPage from "./pages/onboarding/RitualOnboardingPage";
import MythOnboardingWorldPage from "./pages/onboarding/MythOnboardingWorldPage";
import ArchetypeSelectionChamberPage from "./pages/onboarding/ArchetypeSelectionChamberPage";
import SummoningRitualConsolePage from "./pages/onboarding/SummoningRitualConsolePage";
import UserMythpathInitializerPage from "./pages/onboarding/UserMythpathInitializerPage";
import WorldTimelinePage from "./pages/WorldTimelinePage";
import AssistantMythRebirthPage from "./pages/assistants/AssistantMythRebirthPage";
import CodexBriefingPage from "./pages/codex/CodexBriefingPage";
import AssistantTutorialPage from "./pages/assistant/tutorial/AssistantTutorialPage";

import PromptsPage from "./pages/prompts/PromptsPage";
import PromptDetailView from "./pages/prompts/PromptDetailView";
import PromptRemixPage from "./pages/prompts/PromptRemixPage";
import CreatePromptPage from "./pages/prompts/CreatePromptPage";
import PromptCreationAssistant from "./pages/assistant/prompts/PromptCreationAssistant";

// MCP_CORE
import ReflectionPage from "./pages/mcp_core/reflections/ReflectionPage";
import ReflectionHistoryPage from "./pages/mcp_core/reflections/ReflectionHistoryPage";
import ReflectionDetailPage from "./pages/mcp_core/reflections/ReflectionDetailPage";
import ReflectionTagsPage from "./pages/mcp_core/reflections/ReflectionTagsPage";
import HotTagsPage from "./pages/mcp_core/reflections/HotTagsPage";
import RecentReflectionsPage from "./pages/mcp_core/recent/RecentReflectionsPage";
import CustomReflectionPage from "./pages/mcp_core/reflections/CustomReflectionPage";
import PlanningPage from "./pages/dev/PlanningPage";
import ThreadDetailPage from "./pages/mcp_core/threads/ThreadDetailPage";
import ThreadsOverviewPage from "./pages/mcp_core/threads/ThreadsOverviewPage";
import ThreadEditorPage from "./pages/mcp_core/threads/ThreadEditorPage";
import AssistantSessionsPage from "./pages/assistant/sessions/AssistantSessionsPage";
import AssistantSessionDetailPage from "./pages/assistant/sessions/AssistantSessionDetailPage";

{
  /*User Memories */
}
import MemoryBrowserPage from "./pages/memories/entries/MemoryBrowserPage";
import MemoryDetailPage from "./pages/memories/entries/MemoryDetailPage";
import BookmarkedMemoriesPage from "./pages/memories/entries/BookmarkedMemoriesPage";

import MemoryChainBuilderPage from "./pages/memories/chains/MemoryChainBuilderPage";
import MemoryChainViewerPage from "./pages/memories/chains/MemoryChainViewerPage";
import MemoryChainsListPage from "./pages/memories/chains/MemoryChainsListPage";
import MemoryChainDetailPage from "./pages/memories/chains/MemoryChainDetailPage"; // 👈 ADD THIS
import MemoryEntryCreatePage from "./pages/memories/entries/MemoryEntryCreatePage";

{
  /** Assistant */
}
import AssistantDashboardPage from "./pages/assistant/common/AssistantDashboardPage";
import AssistantList from "./pages/assistant/common/AssistantList";
import AssistantDetailPage from "./pages/assistant/common/AssistantDetailPage";
import AssistantThoughtsPage from "./pages/assistant/common/AssistantThoughtsPage";
import AssistantThoughtDetailPage from "./pages/assistant/common/AssistantThoughtDetailPage";
import AssistantDemoPage from "./pages/assistant/common/AssistantDemoPage";
import ChatWithAssistantPage from "./pages/assistant/common/ChatWithAssistantPage";
import CreateNewAssistantPage from "./pages/assistant/common/CreateNewAssistantPage";
import AssistantInterfacePage from "./pages/assistants/AssistantInterfacePage";

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
import AssistantThoughtMapPage from "./pages/assistant/thoughts/AssistantThoughtMap";
import AssistantMemoriesPage from "./pages/assistant/common/AssistantMemoriesPage";
import AssistantMemoryPage from "./pages/assistant/memory/AssistantMemoryPage";
import DelegationTracePage from "./pages/assistant/DelegationTracePage";
import SkillGraphPage from "./pages/assistant/skills/SkillGraphPage";
import MemoryToTaskPage from "./pages/assistant/objectives/MemoryToTaskPage";
import MilestonesPage from "./pages/assistant/milestones/MilestonesPage";
import MilestoneCreatePage from "./pages/assistant/milestones/MilestoneCreatePage";
import MilestoneEditPage from "./pages/assistant/milestones/MilestoneEditPage";
import MemoryChainsPage from "./pages/assistant/memory_chains/MemoryChainsPage";
import MemoryNavigatorPage from "./pages/assistant/analysis/MemoryNavigatorPage";
import ArchetypeAffinityPage from "./pages/assistant/analysis/ArchetypeAffinityPage";
import BeliefEvolutionPage from "./pages/assistant/analysis/BeliefEvolutionPage";

import NextActionsPage from "./pages/assistant/objectives/NextActionsPage";
import ObjectivesPage from "./pages/assistant/objectives/ObjectivesPage";
import PrimaryAssistantDashboard from "./pages/assistants/PrimaryAssistantDashboard";

import AssistantSessionDashboardPage from "./pages/assistant/sessions/AssistantSessionDashboardPage";
import GroupedReflectionsPage from "./pages/mcp_core/reflections/GroupedReflectionsPage";
import SignalSourcesPage from "./pages/assistant/signal_sources/SignalSourcesPage";
import SignalCatchesPage from "./pages/assistant/signal_catches/SignalCatchesPage";
import CouncilDashboardPage from "./pages/assistant/council/CouncilDashboardPage";

import ReflectionsPage from "./pages/assistant/reflections/ReflectionsPage";
import MemoryReflectionPage from "./pages/memories/reflections/MemoryReflectionPage";
import AssistantReflectPage from "./pages/assistant/reflections/AssistantReflectPage";
import AssistantReflectionLogsPage from "./pages/assistant/reflections/AssistantReflectionLogsPage";
import FeedbackSummaryPage from "./pages/assistant/feedback/FeedbackSummaryPage";
import DevDashboard from "./pages/dev/DevDashboard";
import GroupedReflectionPage from "./pages/dev/GroupedReflectionPage";
import GroupedReflectionDetailPage from "./pages/dev/GroupedReflectionDetailPage";
import DocumentBrowserPage from "./pages/intel_core/DocumentBrowserPage";
import DocumentDetailPage from "./pages/intel_core/DocumentDetailPage";
import ImageGalleryPage from "./pages/media/ImageGalleryPage";
import ImageCreatePage from "./pages/media/ImageCreatePage";
import CharacterListPage from "./pages/media/CharacterListPage";
import StoryListPage from "./pages/media/StoryListPage";
import AgentPage from "./pages/agents/AgentPage";
import AgentDetailPage from "./pages/agents/AgentDetailPage";
import AgentArchivePage from "./pages/agents/AgentArchivePage";
import SwarmTimelinePage from "./pages/agents/SwarmTimelinePage";
import RoutingHistoryPage from "./pages/assistants/RoutingHistoryPage";
import StoryboardEditorPage from "./pages/storyboard/StoryboardEditorPage";
import NarrativeEventDetailPage from "./pages/storyboard/NarrativeEventDetailPage";
import RealityShaperDashboard from "./pages/lore/RealityShaperDashboard";
import WorldDashboardPage from "./pages/mythos/WorldDashboardPage";
import AssistantPresenceMapPage from "./pages/mythos/AssistantPresenceMapPage";
import MythflowHeatmapPage from "./pages/mythos/MythflowHeatmapPage";
import MythpathExplorerPage from "./pages/mythos/MythpathExplorerPage";
import SymbolicMemorySynthesizerPage from "./pages/memory/SymbolicMemorySynthesizerPage";
import TemporalReflectionLogsPage from "./pages/reflection/TemporalReflectionLogsPage";

import MotionTestPage from "./pages/ui/MotionTestPage";
import MemoryEchoPage from "./pages/memories/entries/MemoryEchoPage";
import AssistantAuraPage from "./pages/assistant/common/AssistantAuraPage";
import ProphecyEnginePage from "./pages/prophecy/ProphecyEnginePage";
import MemoryPredictionPage from "./pages/memory/MemoryPredictionPage";
import RitualForecastPage from "./pages/ritual/RitualForecastPage";


import { ToastContainer } from "react-toastify";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import ActivityPage from "./pages/ActivityPage";
import "react-toastify/dist/ReactToastify.css";

export default function App() {
  return (
    <Router>
      <div className="d-flex">
        <Sidebar />
        <div className="flex-grow-1">
          <ToastContainer position="bottom-right" autoClose={3000} />
          <Navbar />

          <Routes>
          {/* Auth */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/logout" element={<LogoutPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/onboarding" element={<UserMythpathInitializerPage />} />
          <Route path="/onboarding/world" element={<MythOnboardingWorldPage />} />
          <Route path="/onboarding/archetype" element={<ArchetypeSelectionChamberPage />} />
          <Route path="/onboarding/summon" element={<SummoningRitualConsolePage />} />
          <Route path="/onboarding/wizard" element={<OnboardingWizardPage />} />
          <Route path="/onboarding/ritual" element={<RitualOnboardingPage />} />
          <Route path="/codex/briefing" element={<CodexBriefingPage />} />
          <Route path="/assistant/:id/tutorial" element={<AssistantTutorialPage />} />
          {/* Prompts */}
          <Route path="/" element={<HomePage />} />
          <Route path="/prompts" element={<PromptsPage />} />
          <Route path="/prompts/:slug/remix" element={<PromptRemixPage />} />
          <Route path="/prompts/:slug" element={<PromptDetailView />} />
          <Route path="/prompts/create" element={<CreatePromptPage />} />
          <Route
            path="/prompts/assistant"
            element={<PromptCreationAssistant />}
          />
          {/* Memories */}
          <Route path="/memories/new" element={<MemoryEntryCreatePage />} />
          <Route path="/memories" element={<MemoryBrowserPage />} /> {/* ➕ */}
          <Route path="/memories/bookmarked" element={<BookmarkedMemoriesPage />} />
          <Route path="/memories/:id" element={<MemoryDetailPage />} />{" "}
          <Route path="/memory/:id/echo" element={<MemoryEchoPage />} />
          {/* 🧠 */}
          <Route path="/memories/reflect" element={<MemoryReflectionPage />} />
          <Route path="/memories/chains" element={<MemoryChainsListPage />} />
          <Route
            path="/memories/chains/create"
            element={<MemoryChainBuilderPage />}
          />
          <Route
            path="/memories/chains/:id"
            element={<MemoryChainViewerPage />}
          />
          <Route
            path="/memories/chain/:id"
            element={<MemoryChainDetailPage />}
          />{" "}
          {/* 🔗 Chain Viewer */}
          {/* Assistant & Projects */}
          <Route path="/assistants" element={<AssistantList />} />
          <Route
            path="/assistant-dashboard"
            element={<AssistantDashboardPage />}
          />
          <Route
            path="/assistants/create"
            element={<CreateNewAssistantPage />}
          />
          <Route
            path="/assistants/primary"
            element={<PrimaryAssistantDashboard />}
          />
          <Route
            path="/assistants/primary/dashboard"
            element={<AssistantSessionDashboardPage slug="primary" />}
          />

          {/* Project and Milestone Routes */}
          <Route
            path="/assistants/projects/create"
            element={<CreateProjectPage />}
          />
          <Route
            path="/assistants/projects"
            element={<ProjectsDashboardPage />}
          />
          <Route
            path="/assistants/projects/create-from-memory"
            element={<ProjectCreateFromMemoryPage />}
          />
          <Route
            path="/assistants/projects/:id"
            element={<ProjectDetailPage />}
          />
          <Route
            path="/assistants/projects/:id/build"
            element={<ProjectTaskBuilderPage />}
          />
          <Route
            path="/assistants/projects/:id/edit-tasks"
            element={<ProjectTaskEditor />}
          />
          <Route
            path="/assistants/projects/:id/tasks"
            element={<ProjectTaskManagerPage />}
          />
          <Route
            path="/assistants/projects/:id/status-board"
            element={<ProjectStatusBoardPage />}
          />
          <Route
            path="/assistants/projects/:id/mission"
            element={<ProjectMissionBuilderPage />}
          />
          <Route
            path="/assistants/projects/:projectId/timeline"
            element={<ProjectTimelinePage />}
          />
          <Route
            path="/assistants/projects/:projectId/objectives"
            element={<ProjectObjectivesPage />}
          />
          <Route
            path="/assistants/projects/:projectId/milestones"
            element={<MilestonesPage />}
          />
          <Route
            path="/assistants/projects/:projectId/milestones/create"
            element={<MilestoneCreatePage />}
          />
          <Route
            path="/assistants/projects/:projectId/milestones/:milestoneId/edit"
            element={<MilestoneEditPage />}
          />

          {/* Top-level Assistant Views */}
          <Route
            path="/assistants/projects/:id/thoughts"
            element={<ProjectThoughtLog />}
          />
          <Route
            path="/assistants/next-actions"
            element={<NextActionsPage />}
          />
          <Route
            path="/assistants/memory/:memoryId/to-task"
            element={<MemoryToTaskPage />}
          />
          <Route
            path="/assistants/memory-chains"
            element={<MemoryChainsPage />}
          />
          <Route path="/assistants/reflections" element={<ReflectionsPage />} />
          <Route
            path="/assistants/sessions/"
            element={<AssistantSessionsPage />}
          />
          <Route
            path="/assistants/sessions/:sessionId"
            element={<AssistantSessionDetailPage />}
          />
          <Route path="/assistants/sources" element={<SignalSourcesPage />} />
          <Route path="/assistants/signals" element={<SignalCatchesPage />} />
          <Route path="/assistants/routing-history" element={<RoutingHistoryPage />} />
          <Route path="/assistants/council/:id" element={<CouncilDashboardPage />} />
          <Route path="/assistants-demos" element={<AssistantDemoPage />} />

          {/* Assistant Detail Subroutes */}
          <Route
            path="/assistants/:slug/log_thought"
            element={<AssistantThoughtLogPage />}
          />
          <Route
            path="/assistants/:slug/thoughts/:id"
            element={<AssistantThoughtDetailPage />}
          />
          <Route
            path="/assistants/:slug/thought-map"
            element={<AssistantThoughtMapPage />}
          />
          <Route
            path="/assistants/:slug/timeline"
            element={<MemoryNavigatorPage />}
          />
          <Route
            path="/assistants/:slug/affinity"
            element={<ArchetypeAffinityPage />}
          />
          <Route
            path="/assistants/:slug/belief"
            element={<BeliefEvolutionPage />}
          />
          <Route
            path="/assistants/:slug/memories"
            element={<AssistantMemoriesPage />}
          />
          <Route
            path="/assistants/:slug/memories"
            element={<AssistantMemoryPage />}
          />
          <Route
            path="/assistants/:slug/objectives"
            element={<ObjectivesPage />}
          />
          <Route
            path="/assistants/:slug/reflections"
            element={<AssistantReflectionLogsPage />}
          />
          <Route
            path="/assistants/:slug/reflect"
            element={<AssistantReflectPage />}
          />
          <Route
            path="/assistants/:slug/dashboard"
            element={<AssistantSessionDashboardPage />}
          />
          <Route
            path="/assistants/:slug/sessions"
            element={<AssistantSessionDashboardPage />}
          />
          <Route
            path="/assistants/:slug/delegation-trace"
            element={<DelegationTracePage />}
          />
          <Route
            path="/assistants/:slug/skillgraph"
            element={<SkillGraphPage />}
          />
          <Route
            path="/assistants/:slug/thoughts"
            element={<AssistantThoughtsPage />}
          />
          <Route
            path="/assistants/:slug/feedback"
            element={<FeedbackSummaryPage />}
          />
          <Route
            path="/assistants/:slug/chat"
            element={<ChatWithAssistantPage />}
          />
          <Route
            path="/assistants/:id/interface"
            element={<AssistantInterfacePage />}
          />
          <Route path="/assistants/:id/rebirth" element={<AssistantMythRebirthPage />} />
          <Route path="/assistants/:slug" element={<AssistantDetailPage />} />
          {/* MCP Core */}
          <Route path="/reflect" element={<ReflectionPage />} />
          <Route path="/reflections" element={<ReflectionHistoryPage />} />
          <Route path="/reflections/:id" element={<ReflectionDetailPage />} />
          <Route path="/reflection-tags" element={<ReflectionTagsPage />} />
          <Route
            path="/reflection-tags/:tag"
            element={<ReflectionTagsPage />}
          />
          <Route
            path="/grouped-reflections"
            element={<GroupedReflectionsPage />}
          />
          <Route path="/hot-tags" element={<HotTagsPage />} />
          <Route
            path="/recent-reflections"
            element={<RecentReflectionsPage />}
          />
          <Route path="/activity" element={<ActivityPage />} />
          <Route
            path="/reflections/custom"
            element={<CustomReflectionPage />}
          />
          <Route path="/threads/overview" element={<ThreadsOverviewPage />} />
          <Route path="/threads" element={<ThreadsOverviewPage />} />
          <Route path="/threads/editor" element={<ThreadEditorPage />} />
          <Route path="/threads/:id" element={<ThreadDetailPage />} />
          <Route path="/dev-dashboard" element={<DevDashboard />} />
          <Route path="/planning" element={<PlanningPage />} />
          <Route
            path="/grouped-reflection"
            element={<GroupedReflectionPage />}
          />
          <Route
            path="/grouped-reflection/:id"
            element={<GroupedReflectionDetailPage />}
          />
          <Route path="/agents" element={<AgentPage />} />
          <Route path="/agents/archive" element={<AgentArchivePage />} />
          <Route path="/swarm/timeline" element={<SwarmTimelinePage />} />
          <Route path="/timeline" element={<WorldTimelinePage />} />
          <Route path="/agents/:slug" element={<AgentDetailPage />} />
          <Route path="/intel/documents" element={<DocumentBrowserPage />} />
          <Route path="/intel/documents/:id" element={<DocumentDetailPage />} />
          <Route path="/images" element={<ImageGalleryPage />} />
          <Route path="/images/new" element={<ImageCreatePage />} />
          <Route path="/characters" element={<CharacterListPage />} />
          <Route path="/stories" element={<StoryListPage />} />
          <Route path="/storyboard" element={<StoryboardEditorPage />} />
          <Route path="/storyboard/events/:id" element={<NarrativeEventDetailPage />} />
          <Route path="/dashboard/world" element={<WorldDashboardPage />} />
          <Route path="/map/assistants" element={<AssistantPresenceMapPage />} />
          <Route path="/heatmap/mythflow" element={<MythflowHeatmapPage />} />
          <Route path="/timeline/explore" element={<MythpathExplorerPage />} />
          <Route path="/memory/synthesize" element={<SymbolicMemorySynthesizerPage />} />
          <Route path="/reflection/logs" element={<TemporalReflectionLogsPage />} />
          <Route path="/lore" element={<RealityShaperDashboard />} />

          <Route path="/prophecy/engine" element={<ProphecyEnginePage />} />
          <Route path="/memory/predict" element={<MemoryPredictionPage />} />
          <Route path="/ritual/forecast" element={<RitualForecastPage />} />

          <Route path="/ui/motion" element={<MotionTestPage />} />
          <Route path="/assistants/:id/aura" element={<AssistantAuraPage />} />

          <Route path="/assistants/sources" element={<SignalSourcesPage />} />
          <Route path="/assistants/signals" element={<SignalCatchesPage />} />
          <Route path="/assistants/routing-history" element={<RoutingHistoryPage />} />
          <Route path="/assistants/council/:id" element={<CouncilDashboardPage />} />
        </Routes>
        </div>
      </div>
    </Router>
  );
}
